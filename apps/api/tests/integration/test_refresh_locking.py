from __future__ import annotations

import asyncio
import uuid

import pytest

from app.core.config import Settings
from app.db.session import Database
from app.repositories.refresh_sessions import RefreshSessionRepository

pytestmark = pytest.mark.integration


async def test_refresh_family_lock_serializes_different_token_rows(
    integration_settings: Settings,
) -> None:
    database = Database(integration_settings)
    family_id = uuid.uuid4()
    first_token_id = uuid.uuid4()
    second_token_id = uuid.uuid4()

    try:
        async with database.session_factory() as first_session:
            async with database.session_factory() as second_session:
                first_repository = RefreshSessionRepository(first_session)
                second_repository = RefreshSessionRepository(second_session)

                assert (
                    await first_repository.get_for_update(
                        first_token_id,
                        family_id=family_id,
                    )
                    is None
                )
                blocked_call = asyncio.create_task(
                    second_repository.get_for_update(
                        second_token_id,
                        family_id=family_id,
                    )
                )

                done, _ = await asyncio.wait({blocked_call}, timeout=0.1)
                assert not done

                await first_session.commit()
                assert await asyncio.wait_for(blocked_call, timeout=2) is None
                await second_session.rollback()
    finally:
        await database.dispose()
