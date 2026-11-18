from __future__ import annotations

import logging
import re
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.api.router import root_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.db.session import Database

logger = logging.getLogger(__name__)
_request_id_pattern = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def create_app(settings: Settings | None = None) -> FastAPI:
    actual_settings = settings or get_settings()
    configure_logging()

    database = Database(actual_settings)
    redis = Redis.from_url(actual_settings.redis_url, decode_responses=True)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await redis.aclose()
        await database.dispose()

    application = FastAPI(
        title="CareerRank API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None if actual_settings.app_env == "production" else "/docs",
        redoc_url=None if actual_settings.app_env == "production" else "/redoc",
    )
    application.state.settings = actual_settings
    application.state.database = database
    application.state.redis = redis

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in actual_settings.cors_origins],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Accept", "Content-Type", "X-CSRF-Token", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    @application.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        # FastAPI's default payload includes the rejected input. Omitting it
        # prevents credentials and other sensitive values from being reflected
        # into responses, proxy logs, or browser telemetry.
        safe_errors = [
            {key: error[key] for key in ("type", "loc", "msg") if key in error}
            for error in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": safe_errors})

    @application.middleware("http")
    async def request_logging_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        supplied_request_id = request.headers.get("X-Request-ID", "")
        request_id = (
            supplied_request_id
            if _request_id_pattern.fullmatch(supplied_request_id)
            else str(uuid.uuid4())
        )
        started_at = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            if request.url.path.startswith("/api/v1/auth"):
                response.headers["Cache-Control"] = "no-store, private"
                _append_vary(response, "Cookie")
            return response
        finally:
            logger.info(
                "HTTP request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "latency_ms": round((time.perf_counter() - started_at) * 1000, 2),
                },
            )

    application.include_router(root_router)
    return application


def _append_vary(response: Response, value: str) -> None:
    existing = {
        item.strip() for item in response.headers.get("Vary", "").split(",") if item.strip()
    }
    if value not in existing:
        existing.add(value)
        response.headers["Vary"] = ", ".join(sorted(existing))
