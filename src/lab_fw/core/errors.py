"""Framework error types for lab_fw."""
import httpx

class LabFwError(Exception):
    """Root error for all lab_fw failures."""


class ConfigError(LabFwError):
    """Invalid or missing configuration."""


class ApiError(LabFwError):
    """API / HTTP layer failure."""


class UiError(LabFwError):
    """UI / page / driver layer failure."""

class SchemaError(ApiError):
    """API response schema validation failure."""

class HttpStatusError(ApiError):
    """HTTP response status indicates a failed API request."""
    def __init__(
        self,
        message: str,
        *,
        response: httpx.Response | None = None,
    ) -> None:
        super().__init__(message)
        self.response = response