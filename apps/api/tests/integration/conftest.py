from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic.config import Config
from dotenv import dotenv_values
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import AnyHttpUrl, SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url

from alembic import command
from app.core.config import Settings
from app.db.session import Database
from app.factory import create_app


@pytest.fixture(scope="session")
def integration_settings() -> Settings:
    repository_env = dotenv_values(Path(__file__).resolve().parents[4] / ".env")
    require_integration_value = os.getenv("REQUIRE_INTEGRATION_TESTS")
    if require_integration_value is None:
        require_integration_value = repository_env.get("REQUIRE_INTEGRATION_TESTS") or ""
    require_integration = require_integration_value.lower() in {
        "1",
        "true",
        "yes",
    }
    database_url = os.getenv("TEST_DATABASE_URL") or repository_env.get("TEST_DATABASE_URL")
    redis_url = (
        os.getenv("TEST_REDIS_URL")
        or repository_env.get("TEST_REDIS_URL")
        or os.getenv("REDIS_URL")
        or repository_env.get("REDIS_URL")
    )
    if not database_url or not redis_url:
        if require_integration:
            raise RuntimeError(
                "Integration tests were required, but PostgreSQL/Redis test URLs are missing"
            )
        pytest.skip("TEST_DATABASE_URL and TEST_REDIS_URL are required for integration tests")
    database_name = make_url(database_url).database or ""
    normalized_database_name = database_name.lower()
    if not (
        normalized_database_name.endswith("_test") or normalized_database_name.startswith("test_")
    ):
        raise RuntimeError("TEST_DATABASE_URL must point to a database named test_* or *_test")
    return Settings(
        _env_file=None,
        app_env="test",
        app_url=AnyHttpUrl("http://testserver"),
        cors_origins=[AnyHttpUrl("http://testserver")],
        database_url=database_url,
        redis_url=redis_url,
        jwt_secret=SecretStr("integration-test-secret-that-is-longer-than-32-bytes"),
        cookie_secure=False,
    )


@pytest.fixture(scope="session", autouse=True)
def migrated_database(integration_settings: Settings) -> Iterator[None]:
    api_root = Path(__file__).resolve().parents[2]
    config = Config(str(api_root / "alembic.ini"))
    config.set_main_option("script_location", str(api_root / "alembic"))
    config.set_main_option("sqlalchemy.url", integration_settings.database_url.replace("%", "%%"))
    command.upgrade(config, "head")
    yield


@pytest_asyncio.fixture(autouse=True)
async def clean_database(integration_settings: Settings) -> AsyncIterator[None]:
    database = Database(integration_settings)
    async with database.engine.begin() as connection:
        await connection.execute(
            text("TRUNCATE TABLE refresh_sessions, candidate_profiles, users CASCADE")
        )
    yield
    async with database.engine.begin() as connection:
        await connection.execute(
            text("TRUNCATE TABLE refresh_sessions, candidate_profiles, users CASCADE")
        )
    await database.dispose()


@pytest.fixture
def app(integration_settings: Settings) -> FastAPI:
    return create_app(integration_settings)


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as test_client:
            yield test_client
