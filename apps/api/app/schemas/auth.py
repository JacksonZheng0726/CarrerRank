from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr, field_validator

"""_summary_
defines the data contracts using Pydantic:
- What login/register requests must contain.
- Password validation rules.
- What user/profile/auth responses look like.
- It does not handle HTTP requests or access the database.

HTTP request
    ↓
api/v1/auth.py           Endpoint/controller
    ↓
schemas/auth.py          Validates and structures input
    ↓
services/auth.py         Authentication business logic
    ↓
repositories + models    Database operations

"""

class CredentialsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: SecretStr

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        length = len(value.get_secret_value())
        if not 12 <= length <= 128:
            raise ValueError("Password must be between 12 and 128 characters")
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    created_at: datetime


class CandidateProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    headline: str | None
    years_experience: float | None
    preferred_roles: list[str]
    preferred_locations: list[str]
    work_authorization: dict[str, Any]
    remote_preference: str | None
    created_at: datetime
    updated_at: datetime


class AuthResponse(BaseModel):
    user: UserRead


class MeResponse(BaseModel):
    user: UserRead
    candidate_profile: CandidateProfileRead
