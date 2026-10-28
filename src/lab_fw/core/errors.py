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

class DeadlineExceededError(LabFwError):
    """Deadline exceeded."""


class JobDeadlineExceeded(DeadlineExceededError):
    """Job execution deadline exceeded."""


class WorkerDeadlineExceeded(DeadlineExceededError):
    """Worker execution deadline exceeded."""

class DeviceLabError(LabFwError):
    """Base error for device inventory lab failures."""


class DeviceNotFoundError(DeviceLabError):
    """Requested device does not exist in the inventory."""


class InvalidStateTransitionError(DeviceLabError):
    """Requested device state transition is not allowed."""


class DfuAlreadyInProgressError(DeviceLabError):
    """A firmware update is already in progress for this device."""