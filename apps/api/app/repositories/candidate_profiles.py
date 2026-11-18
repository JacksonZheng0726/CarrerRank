from __future__ import annotations

import uuid
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_profile import CandidateProfile


class CandidateProfileRepository:
    """All profile access is explicitly scoped to the owning user."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_for_user(self, user_id: uuid.UUID) -> CandidateProfile | None:
        return cast(
            CandidateProfile | None,
            await self._session.scalar(
                select(CandidateProfile).where(CandidateProfile.user_id == user_id)
            ),
        )
