import pytest

from device_lab.inventory import InMemoryInventory
from device_lab.models import Device, DeviceState
from lab_fw.core.errors import DeviceNotFoundError
from lab_fw.core.errors import InvalidStateTransitionError
from lab_fw.core.errors import DfuAlreadyInProgressError

@pytest.mark.device_lab
def test_register_creates_offline_device():
    inventory = InMemoryInventory()

    inventory.register("device-001")

    device = inventory.get("device-001")
    assert isinstance(device, Device)
    assert device.device_id == "device-001"
    assert device.firmware_version == "1.0.0"
    assert device.state == DeviceState.OFFLINE
    assert device.last_seen_at is None


@pytest.mark.device_lab
def test_get_unknown_device_raises_error():
    inventory = InMemoryInventory()

    with pytest.raises(DeviceNotFoundError):
        inventory.get("missing-device")


@pytest.mark.device_lab
def test_list_devices_returns_registered_devices():
    inventory = InMemoryInventory()

    inventory.register("device-001")
    inventory.register("device-002", firmware_version="2.0.0")

    devices = inventory.list_devices()
    assert isinstance(devices, list)
    assert len(devices) == 2
    assert {device.device_id for device in devices} == {
        "device-001",
        "device-002",
    }
    assert {device.firmware_version for device in devices} == {
        "1.0.0",
        "2.0.0",
    }

@pytest.mark.device_lab
def test_heartbeat_changes_offline_device_to_online():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    device = inventory.heartbeat("device-001")

    assert device.state == DeviceState.ONLINE
    assert device.last_seen_at is not None


@pytest.mark.device_lab
def test_heartbeat_unknown_device_raises_error():
    inventory = InMemoryInventory()

    with pytest.raises(DeviceNotFoundError):
        inventory.heartbeat("missing-device")

@pytest.mark.device_lab
def test_set_state_changes_online_device_to_offline():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")

    device = inventory.set_state("device-001", DeviceState.OFFLINE)

    assert device.state == DeviceState.OFFLINE


@pytest.mark.device_lab
def test_set_state_rejects_offline_to_dfu_transition():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    with pytest.raises(InvalidStateTransitionError):
        inventory.set_state("device-001", DeviceState.DFU_IN_PROGRESS)


@pytest.mark.device_lab
def test_set_state_rejects_unknown_device():
    inventory = InMemoryInventory()

    with pytest.raises(DeviceNotFoundError):
        inventory.set_state("missing-device", DeviceState.ONLINE)


@pytest.mark.device_lab
def test_start_dfu_changes_online_device_to_dfu_in_progress():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")

    device = inventory.start_dfu("device-001", "2.0.0")

    assert device.state == DeviceState.DFU_IN_PROGRESS
    assert device.firmware_version == "1.0.0"

@pytest.mark.device_lab
def test_start_dfu_rejects_duplicate_request():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")
    inventory.start_dfu("device-001", "2.0.0")

    with pytest.raises(DfuAlreadyInProgressError):
        inventory.start_dfu("device-001", "2.0.0")

@pytest.mark.device_lab
def test_start_dfu_rejects_offline_device():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    with pytest.raises(InvalidStateTransitionError):
        inventory.start_dfu("device-001", "2.0.0")

@pytest.mark.device_lab
def test_start_dfu_rejects_bad_device():
    inventory = InMemoryInventory()

    with pytest.raises(DeviceNotFoundError):
        inventory.start_dfu("bad_device", "2.0.0")



@pytest.mark.device_lab
def test_complete_dfu_updates_firmware_and_returns_online():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")
    inventory.start_dfu("device-001", "2.0.0")

    device = inventory.complete_dfu("device-001", "2.0.0")

    assert device.firmware_version == "2.0.0"
    assert device.state == DeviceState.ONLINE
    assert device.last_seen_at is not None


@pytest.mark.device_lab
def test_complete_dfu_rejects_device_without_active_dfu():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")

    with pytest.raises(InvalidStateTransitionError):
        inventory.complete_dfu("device-001", "2.0.0")

@pytest.mark.device_lab
def test_complete_dfu_rejects_bad_device():
    inventory = InMemoryInventory()

    with pytest.raises(DeviceNotFoundError):
        inventory.complete_dfu("bad_device", "2.0.0")

@pytest.mark.device_lab
def test_fail_dfu_returns_device_online_without_updating_firmware():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")
    inventory.start_dfu("device-001", "2.0.0")

    device = inventory.fail_dfu("device-001")

    assert device.state == DeviceState.ONLINE
    assert device.firmware_version == "1.0.0"


@pytest.mark.device_lab
def test_fail_dfu_rejects_device_without_active_dfu():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")

    with pytest.raises(InvalidStateTransitionError):
        inventory.fail_dfu("device-001")

@pytest.mark.device_lab
def test_fail_dfu_rejects_bad_device():
    inventory = InMemoryInventory()

    with pytest.raises(DeviceNotFoundError):
        inventory.fail_dfu("bad_device")


@pytest.mark.device_lab
def test_set_state_changes_offline_device_to_online():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    device = inventory.set_state("device-001", DeviceState.ONLINE)

    assert device.device_id == "device-001"
    assert device.state == DeviceState.ONLINE
    assert inventory.get("device-001").state == DeviceState.ONLINE


@pytest.mark.device_lab
def test_set_state_changes_online_device_to_offline_2():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")

    device = inventory.set_state("device-001", DeviceState.OFFLINE)

    assert device.device_id == "device-001"
    assert device.state == DeviceState.OFFLINE
    assert inventory.get("device-001").state == DeviceState.OFFLINE


@pytest.mark.device_lab
def test_set_state_rejects_offline_to_dfu_transition_2():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    with pytest.raises(InvalidStateTransitionError):
        inventory.set_state("device-001", DeviceState.DFU_IN_PROGRESS)

    assert inventory.get("device-001").state == DeviceState.OFFLINE


@pytest.mark.device_lab
def test_set_state_rejects_online_to_online_transition():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")

    with pytest.raises(InvalidStateTransitionError):
        inventory.set_state("device-001", DeviceState.ONLINE)

    assert inventory.get("device-001").state == DeviceState.ONLINE


@pytest.mark.device_lab
def test_set_state_rejects_offline_to_offline_transition():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    with pytest.raises(InvalidStateTransitionError):
        inventory.set_state("device-001", DeviceState.OFFLINE)

    assert inventory.get("device-001").state == DeviceState.OFFLINE


@pytest.mark.device_lab
def test_set_state_rejects_dfu_to_online_transition():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")
    inventory.start_dfu("device-001", "2.0.0")

    with pytest.raises(InvalidStateTransitionError):
        inventory.set_state("device-001", DeviceState.ONLINE)

    assert inventory.get("device-001").state == DeviceState.DFU_IN_PROGRESS


@pytest.mark.device_lab
def test_set_state_rejects_unknown_device_2():
    inventory = InMemoryInventory()

    with pytest.raises(DeviceNotFoundError):
        inventory.set_state("missing-device", DeviceState.ONLINE)

@pytest.mark.device_lab
def test_heartbeat_does_not_interrupt_dfu():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")
    inventory.start_dfu("device-001", "2.0.0")

    device = inventory.get("device-001")
    assert device.state == DeviceState.DFU_IN_PROGRESS
    previous_last_seen_at = device.last_seen_at

    inventory.heartbeat("device-001")

    device = inventory.get("device-001")
    assert device.state == DeviceState.DFU_IN_PROGRESS
    assert device.last_seen_at is not None
    assert device.last_seen_at >= previous_last_seen_at

@pytest.mark.device_lab
def test_set_state_online_without_heartbeat_has_no_last_seen_at():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    inventory.set_state("device-001", DeviceState.ONLINE)

    device = inventory.get("device-001")
    assert device.state == DeviceState.ONLINE
    assert device.last_seen_at is None