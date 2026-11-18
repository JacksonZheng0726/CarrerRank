from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import auth_cookie_policy
from app.db.session import Database
from app.models.user import User
from app.services.auth import AuthenticationError, AuthService


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    database = cast(Database, request.app.state.database)
    async for session in database.session():
        try:
            yield session
        except BaseException:
            await session.rollback()
            raise


async def get_current_user(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    access_token = request.cookies.get(auth_cookie_policy(settings).access_name)
    if access_token is None:
        raise _unauthorized()
    try:
        return await AuthService(session, settings).authenticate_access(access_token)
    except AuthenticationError as exc:
        raise _unauthorized() from exc


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication is required",
        headers={"WWW-Authenticate": "Bearer"},
    )


SessionDependency = Annotated[AsyncSession, Depends(get_session)]
SettingsDependency = Annotated[Settings, Depends(get_settings)]
CurrentUser = Annotated[User, Depends(get_current_user)]
