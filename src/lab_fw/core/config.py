"""Settings for lab_fw."""

from __future__ import annotations

import os
from dataclasses import dataclass

from lab_fw.core.errors import ConfigError


@dataclass(frozen=True)
class Settings:
    base_url: str
    timeout_s: float
    log_level: str


def get_settings() -> Settings:
    base_url = os.getenv("LAB_FW_BASE_URL", "https://example.com")
    raw_timeout = os.getenv("LAB_FW_TIMEOUT_S", "5.0")
    log_level = os.getenv("LAB_FW_LOG_LEVEL", "INFO")

    try:
        timeout_s = float(raw_timeout)
    except ValueError as exc:
        raise ConfigError(f"LAB_FW_TIMEOUT_S must be float, got {raw_timeout!r}") from exc

    if timeout_s <= 0:
        raise ConfigError(f"timeout_s must be > 0, got {timeout_s}")

    return Settings(
        base_url=base_url.rstrip("/"),
        timeout_s=timeout_s,
        log_level=log_level.upper(),
    )