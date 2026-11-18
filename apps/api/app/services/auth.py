from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import (
    InvalidTokenError,
    TokenClaims,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_csrf_token,
    hash_password_async,
    hash_secret,
    normalize_email,
    password_needs_rehash,
    secrets_match,
    utc_now,
    values_match,
    verify_dummy_password_async,
    verify_password_async,
)
from app.models.refresh_session import RefreshSession
from app.models.user import User
from app.repositories.refresh_sessions import RefreshSessionRepository
from app.repositories.users import UserRepository

"""_summary_

Performs registration, login, token rotation, logout, and session authentication
Normalizes email addresses.
Hashes and verifies passwords.
Creates access and refresh tokens.
Stores refresh-session hashes in PostgreSQL.
Rotates refresh tokens.
Detects refresh-token reuse and revokes the token family.
Validates CSRF tokens.
Revokes sessions during logout.
Authenticates access tokens.
Controls database commits and rollbacks.
Raises domain errors such as AuthenticationError and DuplicateEmailError

"""

logger = logging.getLogger(__name__)


class AuthenticationError(ValueError):
    """Authentication credentials or a session are invalid."""


class DuplicateEmailError(ValueError):
    """A normalized email address is already registered."""


class CsrfValidationError(ValueError):
    """The submitted CSRF token is missing or does not match its session."""


class RefreshTokenReuseError(AuthenticationError):
    """A rotated refresh token was replayed and its family was revoked."""


@dataclass(frozen=True, slots=True)
class TokenBundle:
    access_token: str
    access_expires_at: datetime
    refresh_token: str
    refresh_expires_at: datetime
    csrf_token: str


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._users = UserRepository(session)
        self._refresh_sessions = RefreshSessionRepository(session)

    async def register(self, *, email: str, password: str) -> tuple[User, TokenBundle]:
        normalized_email = normalize_email(email)
        password_hash = await hash_password_async(password)
        if await self._users.get_by_email(normalized_email) is not None:
            raise DuplicateEmailError("An account with that email already exists")

        try:
            user = await self._users.create(
                email=normalized_email,
                password_hash=password_hash,
            )
            bundle = self._create_session(user_id=user.id)
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            if (
                isinstance(exc.orig, UniqueViolation)
                and exc.orig.diag.constraint_name == "uq_users_email"
            ):
                raise DuplicateEmailError("An account with that email already exists") from exc
            logger.exception("Unexpected integrity violation while registering user")
            raise
        return user, bundle

    async def login(self, *, email: str, password: str) -> tuple[User, TokenBundle]:
        user = await self._users.get_by_email(normalize_email(email))
        # Release the read transaction and its pool connection before running
        # the deliberately expensive password verification.
        await self._session.commit()
        if user is None:
            await verify_dummy_password_async(password)
            raise AuthenticationError("Invalid email or password")
        if not await verify_password_async(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        if password_needs_rehash(user.password_hash):
            user.password_hash = await hash_password_async(password)
        bundle = self._create_session(user_id=user.id)
        await self._session.commit()
        return user, bundle

    async def refresh(
        self,
        *,
        refresh_token: str,
        csrf_cookie: str,
        csrf_header: str,
    ) -> tuple[User, TokenBundle]:
        # Decode signature/claims first, then use the locked database row as the
        # source of truth for expiry so replay of an older token is still detected.
        claims = self._decode_refresh(refresh_token, verify_expiration=False)
        current = await self._refresh_sessions.get_for_update(
            claims.jti,
            family_id=claims.fid,
        )
        current = self._validate_refresh_session(
            current=current,
            refresh_token=refresh_token,
            csrf_cookie=csrf_cookie,
            csrf_header=csrf_header,
            user_id=claims.sub,
            family_id=claims.fid,
        )
        now = utc_now()
        if current.revoked_at is not None:
            await self._refresh_sessions.revoke_family(current.family_id, revoked_at=now)
            await self._session.commit()
            raise RefreshTokenReuseError("Refresh token reuse detected")
        if current.expires_at <= now:
            await self._refresh_sessions.revoke_family(current.family_id, revoked_at=now)
            await self._session.commit()
            raise AuthenticationError("Refresh token has expired")

        user = await self._users.get_by_id(current.user_id)
        if user is None:
            await self._refresh_sessions.revoke_family(current.family_id, revoked_at=now)
            await self._session.commit()
            raise AuthenticationError("Authentication session is invalid")

        replacement_id = uuid.uuid4()
        bundle = self._create_session(
            user_id=user.id,
            family_id=current.family_id,
            session_id=replacement_id,
            now=now,
        )
        # Materialize the replacement before the self-referencing FK is updated.
        await self._session.flush()
        current.revoked_at = now
        current.replaced_by_id = replacement_id
        await self._session.commit()
        return user, bundle

    async def logout(
        self,
        *,
        refresh_token: str,
        csrf_cookie: str,
        csrf_header: str,
    ) -> None:
        claims = self._decode_refresh(refresh_token, verify_expiration=False)
        current = await self._refresh_sessions.get_for_update(
            claims.jti,
            family_id=claims.fid,
        )
        current = self._validate_refresh_session(
            current=current,
            refresh_token=refresh_token,
            csrf_cookie=csrf_cookie,
            csrf_header=csrf_header,
            user_id=claims.sub,
            family_id=claims.fid,
        )
        await self._refresh_sessions.revoke_family(current.family_id, revoked_at=utc_now())
        await self._session.commit()

    async def authenticate_access(self, access_token: str) -> User:
        try:
            claims = decode_token(
                access_token,
                expected_type="access",
                settings=self._settings,
            )
        except InvalidTokenError as exc:
            raise AuthenticationError("Authentication is required") from exc

        if not await self._refresh_sessions.family_is_active(
            claims.fid,
            user_id=claims.sub,
            now=utc_now(),
        ):
            raise AuthenticationError("Authentication session is no longer active")
        user = await self._users.get_by_id(claims.sub, include_profile=True)
        if user is None:
            raise AuthenticationError("Authentication is required")
        return user

    def _create_session(
        self,
        *,
        user_id: uuid.UUID,
        family_id: uuid.UUID | None = None,
        session_id: uuid.UUID | None = None,
        now: datetime | None = None,
    ) -> TokenBundle:
        issued_at = now or utc_now()
        actual_family_id = family_id or uuid.uuid4()
        actual_session_id = session_id or uuid.uuid4()
        refresh_token, refresh_expires_at = create_refresh_token(
            user_id=user_id,
            token_id=actual_session_id,
            family_id=actual_family_id,
            settings=self._settings,
            now=issued_at,
        )
        access_token, access_expires_at = create_access_token(
            user_id=user_id,
            family_id=actual_family_id,
            settings=self._settings,
            now=issued_at,
        )
        csrf_token = generate_csrf_token()
        self._refresh_sessions.add(
            RefreshSession(
                id=actual_session_id,
                family_id=actual_family_id,
                user_id=user_id,
                token_hash=hash_secret(refresh_token),
                csrf_hash=hash_secret(csrf_token),
                expires_at=refresh_expires_at,
            )
        )
        return TokenBundle(
            access_token=access_token,
            access_expires_at=access_expires_at,
            refresh_token=refresh_token,
            refresh_expires_at=refresh_expires_at,
            csrf_token=csrf_token,
        )

    def _decode_refresh(self, token: str, *, verify_expiration: bool = True) -> TokenClaims:
        try:
            return decode_token(
                token,
                expected_type="refresh",
                settings=self._settings,
                verify_expiration=verify_expiration,
            )
        except InvalidTokenError as exc:
            raise AuthenticationError("Refresh token is invalid") from exc

    @staticmethod
    def _validate_refresh_session(
        *,
        current: RefreshSession | None,
        refresh_token: str,
        csrf_cookie: str,
        csrf_header: str,
        user_id: uuid.UUID,
        family_id: uuid.UUID,
    ) -> RefreshSession:
        if current is None or not secrets_match(refresh_token, current.token_hash):
            raise AuthenticationError("Refresh token is invalid")
        if current.user_id != user_id or current.family_id != family_id:
            raise AuthenticationError("Refresh token is invalid")
        if not values_match(csrf_cookie, csrf_header) or not secrets_match(
            csrf_cookie, current.csrf_hash
        ):
            raise CsrfValidationError("CSRF validation failed")
        return current
