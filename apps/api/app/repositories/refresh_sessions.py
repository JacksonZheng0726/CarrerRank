from __future__ import annotations

import uuid
from datetime import datetime
from typing import cast

from sqlalchemy import exists, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_session import RefreshSession


class RefreshSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_for_update(
        self,
        session_id: uuid.UUID,
        *,
        family_id: uuid.UUID,
    ) -> RefreshSession | None:
        # Every mutation in a token family takes the same transaction-scoped
        # lock. A row lock alone cannot protect a replacement row that another
        # transaction has not inserted yet.
        unsigned_key = family_id.int & ((1 << 64) - 1)
        lock_key = unsigned_key if unsigned_key < (1 << 63) else unsigned_key - (1 << 64)
        await self._session.execute(select(func.pg_advisory_xact_lock(lock_key)))
        statement = select(RefreshSession).where(RefreshSession.id == session_id).with_for_update()
        return cast(RefreshSession | None, await self._session.scalar(statement))

    def add(self, refresh_session: RefreshSession) -> None:
        self._session.add(refresh_session)

    async def revoke_family(self, family_id: uuid.UUID, *, revoked_at: datetime) -> None:
        await self._session.execute(
            update(RefreshSession)
            .where(
                RefreshSession.family_id == family_id,
                RefreshSession.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
        )

    async def family_is_active(
        self,
        family_id: uuid.UUID,
        *,
        user_id: uuid.UUID,
        now: datetime,
    ) -> bool:
        statement = select(
            exists().where(
                RefreshSession.family_id == family_id,
                RefreshSession.user_id == user_id,
                RefreshSession.revoked_at.is_(None),
                RefreshSession.expires_at > now,
            )
        )
        return bool(await self._session.scalar(statement))
