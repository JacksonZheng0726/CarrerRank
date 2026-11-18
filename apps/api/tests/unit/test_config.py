from __future__ import annotations

import pytest
from pydantic import SecretStr, ValidationError

from app.core.config import Settings


def test_settings_parse_json_cors_origins_and_blank_cookie_domain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@db:5432/careerrank")
    monkeypatch.setenv("JWT_SECRET", "a-secure-test-secret-that-is-at-least-32-bytes")
    monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:3000","https://app.example.com"]')
    monkeypatch.setenv("COOKIE_DOMAIN", "  ")

    settings = Settings(_env_file=None)

    assert [str(origin).rstrip("/") for origin in settings.cors_origins] == [
        "http://localhost:3000",
        "https://app.example.com",
    ]
    assert settings.cookie_domain is None


def test_settings_reject_short_jwt_secret() -> None:
    with pytest.raises(ValidationError, match="at least 32 bytes"):
        Settings(
            _env_file=None,
            database_url="postgresql+psycopg://user:pass@db:5432/careerrank",
            jwt_secret=SecretStr("short"),
        )


def test_production_requires_secure_cookies() -> None:
    with pytest.raises(ValidationError, match="COOKIE_SECURE"):
        Settings(
            _env_file=None,
            app_env="production",
            database_url="postgresql+psycopg://user:pass@db:5432/careerrank",
            jwt_secret=SecretStr("a-secure-test-secret-that-is-at-least-32-bytes"),
            cookie_secure=False,
        )


def test_settings_reject_parent_domain_cookies() -> None:
    with pytest.raises(ValidationError, match="host-only"):
        Settings(
            _env_file=None,
            database_url="postgresql+psycopg://user:pass@db:5432/careerrank",
            jwt_secret=SecretStr("a-secure-test-secret-that-is-at-least-32-bytes"),
            cookie_domain=".example.com",
        )


def test_settings_reject_samesite_none() -> None:
    with pytest.raises(ValidationError, match="cookie_samesite"):
        Settings.model_validate(
            {
                "database_url": "postgresql+psycopg://user:pass@db:5432/careerrank",
                "jwt_secret": "a-secure-test-secret-that-is-at-least-32-bytes",
                "cookie_samesite": "none",
            }
        )
