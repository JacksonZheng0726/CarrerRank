from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

pytestmark = pytest.mark.integration


async def test_health_endpoints(client: AsyncClient) -> None:
    live_response = await client.get("/health/live")
    assert live_response.status_code == 200
    assert live_response.json() == {"status": "live"}

    ready_response = await client.get("/health/ready")
    assert ready_response.status_code == 200
    assert ready_response.json() == {
        "status": "ready",
        "checks": {"postgres": "up", "redis": "up"},
    }


class UnavailableRedis:
    async def ping(self) -> bool:
        raise ConnectionError("Redis unavailable during readiness test")


async def test_readiness_returns_503_when_redis_is_unavailable(
    app: FastAPI,
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(app.state, "redis", UnavailableRedis())

    response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "checks": {"postgres": "up", "redis": "down"},
    }
