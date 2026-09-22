"""Framework error types for lab_fw."""


class LabFwError(Exception):
    """Root error for all lab_fw failures."""


class ConfigError(LabFwError):
    """Invalid or missing configuration."""


class ApiError(LabFwError):
    """API / HTTP layer failure."""


class UiError(LabFwError):
    """UI / page / driver layer failure."""