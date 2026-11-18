from __future__ import annotations

import uuid
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.candidate_profile import CandidateProfile
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        return cast(
            User | None,
            await self._session.scalar(select(User).where(User.email == email)),
        )

    async def get_by_id(self, user_id: uuid.UUID, *, include_profile: bool = False) -> User | None:
        statement = select(User).where(User.id == user_id)
        if include_profile:
            statement = statement.options(selectinload(User.candidate_profile))
        return cast(User | None, await self._session.scalar(statement))

    async def create(self, *, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        user.candidate_profile = CandidateProfile()
        self._session.add(user)
        await self._session.flush()
        return user
