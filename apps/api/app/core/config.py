from __future__ import annotations

import json
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded exclusively from environment variables."""

    model_config = SettingsConfigDict(
        env_file=("../../.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_url: AnyHttpUrl = AnyHttpUrl("http://localhost:3000")
    cors_origins: Annotated[list[AnyHttpUrl], NoDecode] = [AnyHttpUrl("http://localhost:3000")]
    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: SecretStr
    jwt_issuer: str = "careerrank-api"
    jwt_audience: str = "careerrank-web"
    jwt_access_ttl_minutes: int = Field(default=30, ge=1, le=1440)
    jwt_refresh_ttl_days: int = Field(default=14, ge=1, le=90)

    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict"] = "lax"
    cookie_domain: str | None = None

    sql_echo: bool = False

    @field_validator("database_url")
    @classmethod
    def validate_async_database_url(cls, value: str) -> str:
        if not value.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must use postgresql+psycopg://")
        return value

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, value: str) -> str:
        if not value.startswith(("redis://", "rediss://")):
            raise ValueError("REDIS_URL must use redis:// or rediss://")
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                try:
                    decoded = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ValueError("CORS_ORIGINS contains invalid JSON") from exc
                if not isinstance(decoded, list) or not all(
                    isinstance(origin, str) for origin in decoded
                ):
                    raise ValueError("CORS_ORIGINS JSON value must be a list of strings")
                return decoded
            origins = [origin.strip() for origin in stripped.split(",") if origin.strip()]
            if not origins:
                raise ValueError("CORS_ORIGINS must contain at least one explicit origin")
            return origins
        return value

    @field_validator("cookie_domain", mode="before")
    @classmethod
    def blank_cookie_domain_is_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def validate_security_settings(self) -> Settings:
        secret = self.jwt_secret.get_secret_value()
        if len(secret.encode("utf-8")) < 32:
            raise ValueError("JWT_SECRET must contain at least 32 bytes")
        if self.app_env in {"staging", "production"} and not self.cookie_secure:
            raise ValueError("COOKIE_SECURE must be true outside development and test")
        if self.cookie_domain is not None:
            raise ValueError(
                "COOKIE_DOMAIN is not supported; authentication cookies must be host-only"
            )
        if not self.cors_origins:
            raise ValueError("CORS_ORIGINS must contain at least one explicit origin")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
