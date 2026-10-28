from lab_fw.core.errors import SchemaError
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, ValidationError, Field
from datetime import datetime

class DeviceState(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    DFU_IN_PROGRESS = "dfu_in_progress"

class Device(BaseModel):
    model_config = ConfigDict(
                                        strict=True,
                                        extra="forbid",
                                    )
    device_id: str
    firmware_version: str
    state: DeviceState = Field(strict=False)
    last_seen_at: datetime | None = None

def parse_device(data: dict[str, object]) -> Device:
    try:
        return Device.model_validate(data)
    except ValidationError as exc:
        raise SchemaError(f"Device schema validation failed: {exc}") from exc




