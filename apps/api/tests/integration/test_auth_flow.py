from __future__ import annotations

import uuid
from datetime import timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.security import (
    CSRF_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    create_refresh_token,
    utc_now,
)
from app.factory import create_app

pytestmark = pytest.mark.integration
PASSWORD = "correct-horse-battery-staple"


async def test_invalid_credentials_do_not_reflect_password(client: AsyncClient) -> None:
    submitted_password = "topsecret"
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "candidate@example.com", "password": submitted_password},
    )

    assert response.status_code == 422
    assert submitted_password not in response.text
    assert all(set(error).issubset({"type", "loc", "msg"}) for error in response.json()["detail"])


async def test_production_auth_cookies_use_host_prefix(
    integration_settings: Settings,
) -> None:
    production_settings = integration_settings.model_copy(
        update={"app_env": "production", "cookie_secure": True}
    )
    app = create_app(production_settings)
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="https://testserver",
        ) as production_client:
            response = await production_client.post(
                "/api/v1/auth/register",
                json={"email": "production@example.com", "password": PASSWORD},
            )

    assert response.status_code == 201
    cookies = response.headers.get_list("set-cookie")
    assert any(
        cookie.startswith("__Host-careerrank_access=")
        and "HttpOnly" in cookie
        and "Secure" in cookie
        and "Path=/" in cookie
        and "Domain=" not in cookie
        for cookie in cookies
    )
    assert any(
        cookie.startswith("__Host-careerrank_refresh=")
        and "HttpOnly" in cookie
        and "Secure" in cookie
        and "Path=/" in cookie
        and "Domain=" not in cookie
        for cookie in cookies
    )
    assert any(
        cookie.startswith("__Host-careerrank_csrf=")
        and "HttpOnly" not in cookie
        and "Secure" in cookie
        and "Path=/" in cookie
        and "Domain=" not in cookie
        for cookie in cookies
    )


async def test_register_login_refresh_reuse_logout_flow(
    client: AsyncClient,
    integration_settings: Settings,
) -> None:
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "Candidate@Example.com", "password": PASSWORD},
    )
    assert register_response.status_code == 201
    assert set(register_response.json()) == {"user"}
    assert set(register_response.json()["user"]) == {"id", "email", "created_at"}
    assert register_response.json()["user"]["email"] == "candidate@example.com"

    set_cookie_headers = register_response.headers.get_list("set-cookie")
    access_header = next(value for value in set_cookie_headers if "careerrank_access=" in value)
    refresh_header = next(value for value in set_cookie_headers if "careerrank_refresh=" in value)
    csrf_header = next(value for value in set_cookie_headers if "careerrank_csrf=" in value)
    assert "HttpOnly" in access_header and "Path=/" in access_header
    assert "HttpOnly" in refresh_header and "Path=/api/v1/auth" in refresh_header
    assert "HttpOnly" not in csrf_header and "Path=/" in csrf_header

    me_response = await client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    assert me_response.headers["Cache-Control"] == "no-store, private"
    assert "Cookie" in me_response.headers["Vary"]
    assert me_response.json()["candidate_profile"]["preferred_roles"] == []
    assert me_response.json()["candidate_profile"]["work_authorization"] == {}

    old_refresh_token = client.cookies.get(REFRESH_COOKIE_NAME)
    old_csrf_token = client.cookies.get(CSRF_COOKIE_NAME)
    assert old_refresh_token is not None
    assert old_csrf_token is not None

    missing_csrf_response = await client.post("/api/v1/auth/refresh")
    assert missing_csrf_response.status_code == 403
    assert missing_csrf_response.headers.get_list("set-cookie") == []

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        headers={"X-CSRF-Token": old_csrf_token},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["user"]["email"] == "candidate@example.com"
    assert client.cookies.get(REFRESH_COOKIE_NAME) != old_refresh_token
    assert client.cookies.get(CSRF_COOKIE_NAME) != old_csrf_token

    app = create_app(integration_settings)
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as replay_client:
            replay_client.cookies.set(REFRESH_COOKIE_NAME, old_refresh_token, path="/api/v1/auth")
            replay_client.cookies.set(CSRF_COOKIE_NAME, old_csrf_token, path="/")
            replay_response = await replay_client.post(
                "/api/v1/auth/refresh",
                headers={"X-CSRF-Token": old_csrf_token},
            )
    assert replay_response.status_code == 401

    revoked_family_response = await client.get("/api/v1/auth/me")
    assert revoked_family_response.status_code == 401

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "candidate@example.com", "password": PASSWORD},
    )
    assert login_response.status_code == 200
    new_csrf_token = client.cookies.get(CSRF_COOKIE_NAME)
    assert new_csrf_token is not None

    missing_logout_csrf = await client.post("/api/v1/auth/logout")
    assert missing_logout_csrf.status_code == 403
    assert missing_logout_csrf.headers.get_list("set-cookie") == []

    logout_response = await client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": new_csrf_token},
    )
    assert logout_response.status_code == 204
    after_logout_response = await client.get("/api/v1/auth/me")
    assert after_logout_response.status_code == 401


async def test_csrf_validation_precedes_cookie_clearing(client: AsyncClient) -> None:
    no_csrf_refresh = await client.post("/api/v1/auth/refresh")
    assert no_csrf_refresh.status_code == 403
    assert no_csrf_refresh.headers.get_list("set-cookie") == []

    no_csrf_logout = await client.post("/api/v1/auth/logout")
    assert no_csrf_logout.status_code == 403
    assert no_csrf_logout.headers.get_list("set-cookie") == []

    csrf_token = "caller-controlled-but-matching-csrf-token"
    client.cookies.set(CSRF_COOKIE_NAME, csrf_token, path="/")
    missing_refresh = await client.post(
        "/api/v1/auth/refresh",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert missing_refresh.status_code == 401

    client.cookies.set(CSRF_COOKIE_NAME, csrf_token, path="/")
    missing_logout = await client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert missing_logout.status_code == 204


async def test_logout_is_idempotent_for_invalid_or_expired_session(
    client: AsyncClient,
    integration_settings: Settings,
) -> None:
    invalid_csrf = "invalid-session-csrf-token"
    client.cookies.set(REFRESH_COOKIE_NAME, "not-a-jwt", path="/api/v1/auth")
    client.cookies.set(CSRF_COOKIE_NAME, invalid_csrf, path="/")
    invalid_response = await client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": invalid_csrf},
    )
    assert invalid_response.status_code == 204

    expired_csrf = "expired-session-csrf-token"
    issued_at = utc_now() - timedelta(days=integration_settings.jwt_refresh_ttl_days + 1)
    expired_token, _ = create_refresh_token(
        user_id=uuid.uuid4(),
        token_id=uuid.uuid4(),
        family_id=uuid.uuid4(),
        settings=integration_settings,
        now=issued_at,
    )
    client.cookies.set(REFRESH_COOKIE_NAME, expired_token, path="/api/v1/auth")
    client.cookies.set(CSRF_COOKIE_NAME, expired_csrf, path="/")
    expired_response = await client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": expired_csrf},
    )
    assert expired_response.status_code == 204


async def test_duplicate_registration_and_invalid_login(client: AsyncClient) -> None:
    payload = {"email": "candidate@example.com", "password": PASSWORD}
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 409
    invalid_login = await client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": "incorrect-password-value"},
    )
    assert invalid_login.status_code == 401
