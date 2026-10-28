from device_lab.models import Device, DeviceState, parse_device
from lab_fw.core.errors import (
                                    DeviceNotFoundError,
                                    InvalidStateTransitionError,
                                    DfuAlreadyInProgressError,
                                )
from datetime import datetime, timezone

class InMemoryInventory:
    def __init__(self):
        self._devices = {}

    @property
    def devices(self):
        return self._devices

    def register(self, device_id: str, firmware_version: str = "1.0.0") -> None:
        self.devices[device_id] = parse_device(
                                                    {
                                                        "device_id": device_id,
                                                        "firmware_version": firmware_version,
                                                        "state": DeviceState.OFFLINE,
                                                    }
                                               
                                               )

    def get(self, device_id: str) -> Device:
        try:
            return self.devices[device_id]
        except KeyError as exc:
            raise DeviceNotFoundError(f'Device: "{device_id}" not found') from exc

    def list_devices(self) -> list[Device]:
        return list(self.devices.values())

    def heartbeat(self, device_id: str) -> Device:
        device = self.get(device_id)
        
        if device.state != DeviceState.DFU_IN_PROGRESS:
            device.state = DeviceState.ONLINE
        device.last_seen_at = datetime.now(timezone.utc)
        return device

    def set_state(self, device_id: str, state: DeviceState) -> Device:
        device = self.get(device_id)
        allowed_transitions = {
            DeviceState.OFFLINE: {DeviceState.ONLINE},
            DeviceState.ONLINE: {DeviceState.OFFLINE},
            DeviceState.DFU_IN_PROGRESS: set(),
        }

        if state not in allowed_transitions[device.state]:
            raise InvalidStateTransitionError(
                f"Cannot change device state from "
                f"{device.state.value} to {state.value}"
            )

        device.state = state
        return device


    def start_dfu(self, device_id: str, target_version: str) -> Device:
        device = self.get(device_id)

        if device.state == DeviceState.DFU_IN_PROGRESS:
            raise DfuAlreadyInProgressError(
                f'DFU is already in progress for device "{device_id}"'
            )

        if device.state != DeviceState.ONLINE:
            raise InvalidStateTransitionError(
                f"Cannot start DFU while device is {device.state.value}"
            )

        device.state = DeviceState.DFU_IN_PROGRESS
        return device

    def complete_dfu(self, device_id: str, new_version: str) -> Device:
        device = self.get(device_id)

        if device.state != DeviceState.DFU_IN_PROGRESS:
            raise InvalidStateTransitionError(
                f"Cannot complete DFU while device is {device.state.value}"
            )

        device.firmware_version = new_version
        device.state = DeviceState.ONLINE
        device.last_seen_at = datetime.now(timezone.utc)

        return device

    def fail_dfu(self, device_id: str) -> Device:
        device = self.get(device_id)


        if device.state != DeviceState.DFU_IN_PROGRESS:
            raise InvalidStateTransitionError(
                f"Cannot fail DFU while device is {device.state.value}"
            )

        device.state = DeviceState.ONLINE
        return device