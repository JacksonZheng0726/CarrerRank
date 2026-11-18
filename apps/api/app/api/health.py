from __future__ import annotations

import asyncio
import logging
from typing import Literal, Protocol, cast

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text

from app.db.session import Database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


class RedisHealthClient(Protocol):
    async def ping(self) -> bool: ...


class LiveResponse(BaseModel):
    status: Literal["live"] = "live"


class DependencyChecks(BaseModel):
    postgres: Literal["up", "down"]
    redis: Literal["up", "down"]


class ReadyResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    checks: DependencyChecks


@router.get("/live", response_model=LiveResponse)
async def live() -> LiveResponse:
    return LiveResponse()


@router.get(
    "/ready",
    response_model=ReadyResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadyResponse}},
)
async def ready(request: Request) -> ReadyResponse | JSONResponse:
    postgres_up, redis_up = await asyncio.gather(
        _postgres_is_ready(request),
        _redis_is_ready(request),
    )
    payload = ReadyResponse(
        status="ready" if postgres_up and redis_up else "not_ready",
        checks=DependencyChecks(
            postgres="up" if postgres_up else "down",
            redis="up" if redis_up else "down",
        ),
    )
    if postgres_up and redis_up:
        return payload
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload.model_dump(mode="json"),
    )


async def _postgres_is_ready(request: Request) -> bool:
    database = cast(Database, request.app.state.database)
    try:
        async with asyncio.timeout(2.0):
            async with database.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.warning("PostgreSQL readiness check failed", exc_info=True)
        return False


async def _redis_is_ready(request: Request) -> bool:
    redis = cast(RedisHealthClient, request.app.state.redis)
    try:
        async with asyncio.timeout(2.0):
            result = await redis.ping()
        return bool(result)
    except Exception:
        logger.warning("Redis readiness check failed", exc_info=True)
        return False
