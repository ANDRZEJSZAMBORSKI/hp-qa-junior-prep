"""Test data factories for users."""

from __future__ import annotations

from typing import Any


def make_user(**overrides: Any) -> dict[str, Any]:
    """Build a user payload; override any field via kwargs."""
    user = {
        "email": "user@example.com",
        "name": "Test User",
        "role": "user",
        "active": True,
    }
    user.update(overrides)
    return user