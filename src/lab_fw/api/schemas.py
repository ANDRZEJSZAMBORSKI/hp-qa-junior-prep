"""Pydantic schemas for API responses."""

from pydantic import BaseModel, ConfigDict, ValidationError

from lab_fw.core.errors import SchemaError


class User(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    id: int
    name: str


class TokenResponse(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    access_token: str
    token_type: str
    expires_in: int


def parse_user(data: dict) -> User:
    try:
        return User.model_validate(data)
    except ValidationError as exc:
        raise SchemaError(f"User schema validation failed: {exc}") from exc


def parse_token(data: dict) -> TokenResponse:
    try:
        return TokenResponse.model_validate(data)
    except ValidationError as exc:
        raise SchemaError(f"TokenResponse schema validation failed: {exc}") from exc