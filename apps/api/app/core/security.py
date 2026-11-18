from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt
from anyio import CapacityLimiter, to_thread
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from pydantic import BaseModel, ValidationError

from app.core.config import Settings

JWT_ALGORITHM = "HS256"
ACCESS_COOKIE_NAME = "careerrank_access"
REFRESH_COOKIE_NAME = "careerrank_refresh"
CSRF_COOKIE_NAME = "careerrank_csrf"
REFRESH_COOKIE_PATH = "/api/v1/auth"
HOST_ACCESS_COOKIE_NAME = "__Host-careerrank_access"
HOST_REFRESH_COOKIE_NAME = "__Host-careerrank_refresh"
HOST_CSRF_COOKIE_NAME = "__Host-careerrank_csrf"

_password_hasher = PasswordHasher()
_dummy_password_hash = _password_hasher.hash(secrets.token_urlsafe(32))
_password_work_limiter = CapacityLimiter(4)


class TokenClaims(BaseModel):
    sub: uuid.UUID
    jti: uuid.UUID
    fid: uuid.UUID
    type: Literal["access", "refresh"]
    iss: str
    aud: str
    iat: datetime
    nbf: datetime
    exp: datetime


class InvalidTokenError(ValueError):
    """Raised when a JWT is invalid or has the wrong token type."""


@dataclass(frozen=True, slots=True)
class AuthCookiePolicy:
    access_name: str
    refresh_name: str
    csrf_name: str
    refresh_path: str


def auth_cookie_policy(settings: Settings) -> AuthCookiePolicy:
    if settings.app_env in {"staging", "production"}:
        return AuthCookiePolicy(
            access_name=HOST_ACCESS_COOKIE_NAME,
            refresh_name=HOST_REFRESH_COOKIE_NAME,
            csrf_name=HOST_CSRF_COOKIE_NAME,
            refresh_path="/",
        )
    return AuthCookiePolicy(
        access_name=ACCESS_COOKIE_NAME,
        refresh_name=REFRESH_COOKIE_NAME,
        csrf_name=CSRF_COOKIE_NAME,
        refresh_path=REFRESH_COOKIE_PATH,
    )


def utc_now() -> datetime:
    return datetime.now(UTC)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def verify_dummy_password(password: str) -> None:
    """Consume a normal Argon2 verification for unknown accounts."""

    verify_password(password, _dummy_password_hash)


def password_needs_rehash(password_hash: str) -> bool:
    try:
        return _password_hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return True


async def hash_password_async(password: str) -> str:
    return await to_thread.run_sync(
        hash_password,
        password,
        limiter=_password_work_limiter,
    )


async def verify_password_async(password: str, password_hash: str) -> bool:
    return await to_thread.run_sync(
        verify_password,
        password,
        password_hash,
        limiter=_password_work_limiter,
    )


async def verify_dummy_password_async(password: str) -> None:
    await to_thread.run_sync(
        verify_dummy_password,
        password,
        limiter=_password_work_limiter,
    )


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def secrets_match(value: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_secret(value), expected_hash)


def values_match(left: str, right: str) -> bool:
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def create_access_token(
    *,
    user_id: uuid.UUID,
    family_id: uuid.UUID,
    settings: Settings,
    now: datetime | None = None,
) -> tuple[str, datetime]:
    issued_at = now or utc_now()
    expires_at = issued_at + timedelta(minutes=settings.jwt_access_ttl_minutes)
    token = _encode_token(
        user_id=user_id,
        token_id=uuid.uuid4(),
        family_id=family_id,
        kind="access",
        issued_at=issued_at,
        expires_at=expires_at,
        settings=settings,
    )
    return token, expires_at


def create_refresh_token(
    *,
    user_id: uuid.UUID,
    token_id: uuid.UUID,
    family_id: uuid.UUID,
    settings: Settings,
    now: datetime | None = None,
) -> tuple[str, datetime]:
    issued_at = now or utc_now()
    expires_at = issued_at + timedelta(days=settings.jwt_refresh_ttl_days)
    token = _encode_token(
        user_id=user_id,
        token_id=token_id,
        family_id=family_id,
        kind="refresh",
        issued_at=issued_at,
        expires_at=expires_at,
        settings=settings,
    )
    return token, expires_at


def _encode_token(
    *,
    user_id: uuid.UUID,
    token_id: uuid.UUID,
    family_id: uuid.UUID,
    kind: Literal["access", "refresh"],
    issued_at: datetime,
    expires_at: datetime,
    settings: Settings,
) -> str:
    payload = {
        "sub": str(user_id),
        "jti": str(token_id),
        "fid": str(family_id),
        "type": kind,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": issued_at,
        "nbf": issued_at,
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )


def decode_token(
    token: str,
    *,
    expected_type: Literal["access", "refresh"],
    settings: Settings,
    verify_expiration: bool = True,
) -> TokenClaims:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
            options={
                "require": ["sub", "jti", "fid", "type", "iss", "aud", "iat", "nbf", "exp"],
                "verify_exp": verify_expiration,
            },
        )
        claims = TokenClaims.model_validate(payload)
    except (jwt.PyJWTError, ValidationError, ValueError, TypeError) as exc:
        raise InvalidTokenError("Invalid authentication token") from exc
    if claims.type != expected_type:
        raise InvalidTokenError("Invalid authentication token type")
    return claims
