import pytest
from datetime import datetime, timezone

from device_lab.models import Device, DeviceState, parse_device
from lab_fw.core.errors import SchemaError


@pytest.mark.device_lab
def test_parse_device_accepts_valid_data():
    data = {
        "device_id": "device-001",
        "firmware_version": "1.0.0",
        "state": "offline",
    }

    device = parse_device(data)
    assert isinstance(device, Device)
    assert device.device_id == "device-001"
    assert device.firmware_version == "1.0.0"
    assert device.state == DeviceState.OFFLINE
    assert device.last_seen_at is None


@pytest.mark.device_lab
def test_parse_device_accepts_datetime():
    timestamp = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)

    data = {
        "device_id": "device-001",
        "firmware_version": "1.0.0",
        "state": "online",
        "last_seen_at": timestamp,
    }

    device = parse_device(data)
    assert isinstance(device, Device)
    assert device.device_id == "device-001"
    assert device.firmware_version == "1.0.0"
    assert device.state == DeviceState.ONLINE
    assert device.last_seen_at == timestamp


@pytest.mark.device_lab
def test_parse_device_rejects_missing_required_field():
    data = {
        "device_id": "device-001",
        "state": "offline",
    }

    with pytest.raises(SchemaError):
        parse_device(data)


@pytest.mark.device_lab
def test_parse_device_rejects_unknown_field():
    data = {
        "device_id": "device-001",
        "firmware_version": "1.0.0",
        "state": "offline",
        "unexpected_field": "value",
    }

    with pytest.raises(SchemaError):
        parse_device(data)


@pytest.mark.device_lab
def test_parse_device_rejects_invalid_state():
    data = {
        "device_id": "device-001",
        "firmware_version": "1.0.0",
        "state": "broken",
    }

    with pytest.raises(SchemaError):
        parse_device(data)
