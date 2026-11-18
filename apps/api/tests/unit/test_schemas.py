from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.auth import CredentialsRequest


def test_credentials_validate_email_and_password() -> None:
    credentials = CredentialsRequest.model_validate(
        {
            "email": "Candidate@Example.com",
            "password": "correct-horse-battery-staple",
        }
    )
    assert str(credentials.email) == "Candidate@example.com"


@pytest.mark.parametrize(
    ("payload", "expected_message"),
    [
        (
            {"email": "not-an-email", "password": "correct-horse-battery-staple"},
            "valid email",
        ),
        ({"email": "candidate@example.com", "password": "too-short"}, "between 12 and 128"),
    ],
)
def test_credentials_reject_invalid_input(payload: dict[str, str], expected_message: str) -> None:
    with pytest.raises(ValidationError, match=expected_message):
        CredentialsRequest.model_validate(payload)


def test_credentials_forbid_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        CredentialsRequest.model_validate(
            {
                "email": "candidate@example.com",
                "password": "correct-horse-battery-staple",
                "admin": True,
            }
        )
