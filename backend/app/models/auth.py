"""Typed API and persistence contracts for role-aware authentication."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Role = Literal["agent", "admin"]


class Principal(BaseModel):
    """The minimum identity carried by a validated bearer token."""

    account_id: int = Field(gt=0)
    role: Role


class AccountRecord(BaseModel):
    """Internal row shape returned by the authentication repository."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Role
    email: str
    password_hash: str
    name: str
    region: str | None = None
    pincode: str | None = None
    deleted_at: datetime | None = None


class AccountResponse(BaseModel):
    """Public account representation; password hashes never leave the service."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Role
    email: str
    name: str
    region: str | None = None
    pincode: str | None = None


class AgentSignupRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    region: str = Field(default="", max_length=100)
    pincode: str = Field(pattern=r"^[0-9]{6}$")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("email must be valid")
        return normalized


class AdminSignupRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("email must be valid")
        return normalized


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("email must be valid")
        return normalized


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    account: AccountResponse


# Backwards-compatible descriptive aliases for callers that prefer explicit names.
AgentSignup = AgentSignupRequest
AdminSignup = AdminSignupRequest
Credentials = LoginRequest
