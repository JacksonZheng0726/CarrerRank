from __future__ import annotations

import asyncio
import threading
import uuid
from datetime import timedelta

import pytest
from pydantic import SecretStr

import app.core.security as security_module
from app.core.config import Settings
from app.core.security import (
    InvalidTokenError,
    auth_cookie_policy,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_secret,
    secrets_match,
    utc_now,
    verify_password,
    verify_password_async,
)


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        app_env="test",
        database_url="postgresql+psycopg://user:pass@db:5432/careerrank_test",
        jwt_secret=SecretStr("a-secure-test-secret-that-is-at-least-32-bytes"),
    )


def test_passwords_use_argon2id_and_verify() -> None:
    password_hash = hash_password("correct-horse-battery-staple")
    assert password_hash.startswith("$argon2id$")
    assert verify_password("correct-horse-battery-staple", password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_production_cookie_policy_uses_host_prefix() -> None:
    production_settings = Settings(
        _env_file=None,
        app_env="production",
        database_url="postgresql+psycopg://user:pass@db:5432/careerrank",
        jwt_secret=SecretStr("a-secure-test-secret-that-is-at-least-32-bytes"),
        cookie_secure=True,
    )

    policy = auth_cookie_policy(production_settings)

    assert policy.access_name == "__Host-careerrank_access"
    assert policy.refresh_name == "__Host-careerrank_refresh"
    assert policy.csrf_name == "__Host-careerrank_csrf"
    assert policy.refresh_path == "/"


async def test_password_work_is_bounded_and_does_not_block_event_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    active = 0
    peak_active = 0
    state_lock = threading.Lock()
    event_loop = asyncio.get_running_loop()
    workers_at_capacity = asyncio.Event()
    release_workers = threading.Event()

    def slow_verify(_: str, __: str) -> bool:
        nonlocal active, peak_active
        with state_lock:
            active += 1
            peak_active = max(peak_active, active)
            if active == 4:
                event_loop.call_soon_threadsafe(workers_at_capacity.set)
        try:
            release_workers.wait(timeout=0.5)
        finally:
            with state_lock:
                active -= 1
        return True

    monkeypatch.setattr(security_module, "verify_password", slow_verify)
    tasks = [asyncio.create_task(verify_password_async("password", "hash")) for _ in range(8)]
    event_loop_tick_seen = False
    try:
        async with asyncio.timeout(2):
            await workers_at_capacity.wait()
            await asyncio.sleep(0)
            event_loop_tick_seen = True
    finally:
        release_workers.set()
        results = await asyncio.gather(*tasks)

    assert event_loop_tick_seen
    assert all(results)
    assert 1 < peak_active <= 4


def test_secret_hash_comparison() -> None:
    expected_hash = hash_secret("refresh-token")
    assert len(expected_hash) == 64
    assert secrets_match("refresh-token", expected_hash)
    assert not secrets_match("different-token", expected_hash)


def test_access_token_round_trip(settings: Settings) -> None:
    user_id = uuid.uuid4()
    family_id = uuid.uuid4()
    token, _ = create_access_token(
        user_id=user_id,
        family_id=family_id,
        settings=settings,
    )
    claims = decode_token(token, expected_type="access", settings=settings)
    assert claims.sub == user_id
    assert claims.fid == family_id
    assert claims.type == "access"


def test_token_type_is_enforced(settings: Settings) -> None:
    token, _ = create_refresh_token(
        user_id=uuid.uuid4(),
        token_id=uuid.uuid4(),
        family_id=uuid.uuid4(),
        settings=settings,
    )
    with pytest.raises(InvalidTokenError):
        decode_token(token, expected_type="access", settings=settings)


def test_expired_access_token_is_rejected(settings: Settings) -> None:
    issued_at = utc_now() - timedelta(minutes=settings.jwt_access_ttl_minutes + 1)
    token, _ = create_access_token(
        user_id=uuid.uuid4(),
        family_id=uuid.uuid4(),
        settings=settings,
        now=issued_at,
    )
    with pytest.raises(InvalidTokenError):
        decode_token(token, expected_type="access", settings=settings)
