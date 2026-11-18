from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from app.api.dependencies import CurrentUser, SessionDependency, SettingsDependency
from app.core.config import Settings
from app.core.security import (
    auth_cookie_policy,
    values_match,
)
from app.schemas.auth import AuthResponse, CredentialsRequest, MeResponse, UserRead
from app.services.auth import (
    AuthenticationError,
    AuthService,
    CsrfValidationError,
    DuplicateEmailError,
    RefreshTokenReuseError,
    TokenBundle,
)

"""
defines the HTTP endpoints:
- POST /register
- POST /login
- POST /refresh
- POST /logout
- GET /me
- It reads requests and cookies, applies CSRF checks, calls AuthService, sets status codes, and creates or clears authentication cookies.

"""

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: CredentialsRequest,
    response: Response,
    session: SessionDependency,
    settings: SettingsDependency,
) -> AuthResponse:
    try:
        user, tokens = await AuthService(session, settings).register(
            email=str(payload.email),
            password=payload.password.get_secret_value(),
        )
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    _set_auth_cookies(response, tokens, settings)
    return AuthResponse(user=UserRead.model_validate(user))


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: CredentialsRequest,
    response: Response,
    session: SessionDependency,
    settings: SettingsDependency,
) -> AuthResponse:
    try:
        user, tokens = await AuthService(session, settings).login(
            email=str(payload.email),
            password=payload.password.get_secret_value(),
        )
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from exc
    _set_auth_cookies(response, tokens, settings)
    return AuthResponse(user=UserRead.model_validate(user))


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    request: Request,
    session: SessionDependency,
    settings: SettingsDependency,
    csrf_header: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> AuthResponse | Response:
    policy = auth_cookie_policy(settings)
    refresh_token = request.cookies.get(policy.refresh_name)
    csrf_cookie = request.cookies.get(policy.csrf_name)
    if not csrf_cookie or not csrf_header or not values_match(csrf_cookie, csrf_header):
        return _csrf_error_response()
    if refresh_token is None:
        return _auth_error_response(settings)
    try:
        user, tokens = await AuthService(session, settings).refresh(
            refresh_token=refresh_token,
            csrf_cookie=csrf_cookie,
            csrf_header=csrf_header,
        )
    except CsrfValidationError:
        return _csrf_error_response()
    except RefreshTokenReuseError:
        logger.warning("Refresh-token reuse detected; revoked token family")
        return _auth_error_response(settings)
    except AuthenticationError:
        return _auth_error_response(settings)

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content=AuthResponse(user=UserRead.model_validate(user)).model_dump(mode="json"),
    )
    _set_auth_cookies(response, tokens, settings)
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def logout(
    request: Request,
    session: SessionDependency,
    settings: SettingsDependency,
    csrf_header: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> Response:
    policy = auth_cookie_policy(settings)
    refresh_token = request.cookies.get(policy.refresh_name)
    csrf_cookie = request.cookies.get(policy.csrf_name)
    if not csrf_cookie or not csrf_header or not values_match(csrf_cookie, csrf_header):
        return _csrf_error_response()
    if refresh_token is None:
        return _logout_response(settings)
    try:
        await AuthService(session, settings).logout(
            refresh_token=refresh_token,
            csrf_cookie=csrf_cookie,
            csrf_header=csrf_header,
        )
    except CsrfValidationError:
        return _csrf_error_response()
    except AuthenticationError:
        return _logout_response(settings)

    return _logout_response(settings)


@router.get("/me", response_model=MeResponse)
async def me(current_user: CurrentUser) -> MeResponse:
    return MeResponse.model_validate(
        {
            "user": current_user,
            "candidate_profile": current_user.candidate_profile,
        }
    )


def _set_auth_cookies(response: Response, tokens: TokenBundle, settings: Settings) -> None:
    policy = auth_cookie_policy(settings)
    response.set_cookie(
        key=policy.access_name,
        value=tokens.access_token,
        httponly=True,
        path="/",
        expires=tokens.access_expires_at,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
    response.set_cookie(
        key=policy.refresh_name,
        value=tokens.refresh_token,
        httponly=True,
        path=policy.refresh_path,
        expires=tokens.refresh_expires_at,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
    response.set_cookie(
        key=policy.csrf_name,
        value=tokens.csrf_token,
        httponly=False,
        path="/",
        expires=tokens.refresh_expires_at,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


def _clear_auth_cookies(response: Response, settings: Settings) -> None:
    policy = auth_cookie_policy(settings)
    response.delete_cookie(
        policy.access_name,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
    response.delete_cookie(
        policy.refresh_name,
        path=policy.refresh_path,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
    response.delete_cookie(
        policy.csrf_name,
        path="/",
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


def _auth_error_response(settings: Settings) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Authentication session is invalid"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    _clear_auth_cookies(response, settings)
    return response


def _csrf_error_response() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "CSRF validation failed"},
    )


def _logout_response(settings: Settings) -> Response:
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_auth_cookies(response, settings)
    return response
