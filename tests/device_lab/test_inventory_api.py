import httpx
import pytest
from device_lab.models import Device, DeviceState
from device_lab.api import create_handler
from device_lab.inventory import InMemoryInventory
from lab_fw.api.client import ApiClient
from lab_fw.core.config import Settings


@pytest.mark.device_lab
def test_get_device_returns_device_json():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/devices/device-001")

    assert response.status_code == 200
    assert response.json()["device_id"] == "device-001"
    assert response.json()["firmware_version"] == "1.0.0"
    assert response.json()["state"] == "offline"
    assert response.request.method == "GET"
    assert response.request.url.path == "/devices/device-001"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/device-001"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }
    
@pytest.mark.device_lab
def test_get_bad_device():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/devices/missing-device")

    assert response.status_code == 404
    assert response.json() == {"error": "device_not_found"}
    assert "device_id" not in response.json()
    assert response.request.method == "GET"
    assert response.request.url.path == "/devices/missing-device"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/missing-device"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }


@pytest.mark.device_lab
def test_unknown_route_returns_404():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/bad_devices/device-001")

    assert response.status_code == 404
    assert response.json() == {"error": "not_found"}
    assert "device_id" not in response.json()
    assert response.request.method == "GET"
    assert response.request.url.path == "/bad_devices/device-001"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/bad_devices/device-001"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }


@pytest.mark.device_lab
def test_get_devices_returns_all_registered_devices():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.register("device-002", firmware_version="2.0.0")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
        base_url="https://device-cloud.test",
        timeout_s=5.0,
        log_level="INFO",
    )

    with ApiClient(settings, transport=transport) as client:
        response = client.get("/devices")

    assert response.status_code == 200

    devices = response.json()
    assert len(devices) == 2
    assert {device["device_id"] for device in devices} == {
        "device-001",
        "device-002",
    }
    assert devices == [
    {
        "device_id": "device-001",
        "firmware_version": "1.0.0",
        "state": "offline",
        "last_seen_at": None,
    },
    {
        "device_id": "device-002",
        "firmware_version": "2.0.0",
        "state": "offline",
        "last_seen_at": None,
    },
]

@pytest.mark.device_lab
def test_post_heartbeat_returns_online_device():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )
    device = inventory.get("device-001")
    assert isinstance(device, Device)
    assert device.device_id == "device-001"
    assert device.firmware_version == "1.0.0"
    assert device.state == DeviceState.OFFLINE
    assert device.last_seen_at is None
    
    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/device-001/heartbeat")

    device = inventory.get("device-001")
    assert device.state == DeviceState.ONLINE

    assert response.status_code == 200
    assert response.json()["device_id"] == "device-001"
    assert response.json()["firmware_version"] == "1.0.0"
    assert response.json()["state"] == "online"
    assert response.json()["last_seen_at"] is not None
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/device-001/heartbeat"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/device-001/heartbeat"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }
    
@pytest.mark.device_lab
def test_post_bad_device():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/missing-device/heartbeat")

    assert response.status_code == 404
    assert response.json() == {"error": "device_not_found"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/missing-device/heartbeat"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/missing-device/heartbeat"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }


@pytest.mark.device_lab
def test_post_unknown_route_returns_404():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/bad_devices/device-001/heartbeat")

    assert response.status_code == 404
    assert response.json() == {"error": "not_found"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/bad_devices/device-001/heartbeat"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/bad_devices/device-001/heartbeat"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }


@pytest.mark.device_lab
def test_post_start_dfu_returns_online_device():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")
    
    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )
    device = inventory.get("device-001")
    assert isinstance(device, Device)
    assert device.device_id == "device-001"
    assert device.firmware_version == "1.0.0"
    assert device.state == DeviceState.ONLINE
    assert device.last_seen_at is not None
    
    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/device-001/dfu/start", json={"target_version": "2.0.0"})

    device = inventory.get("device-001")
    assert device.state == DeviceState.DFU_IN_PROGRESS
    assert device.firmware_version == "1.0.0"

    assert response.status_code == 200
    assert response.json()["device_id"] == "device-001"
    assert response.json()["firmware_version"] == "1.0.0"
    assert response.json()["state"] == "dfu_in_progress"
    assert response.json()["last_seen_at"] is not None
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/device-001/dfu/start"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/device-001/dfu/start"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }
    
@pytest.mark.device_lab
def test_post_start_dfu_bad_device():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/missing-device/dfu/start", json={"target_version": "2.0.0"})

    assert response.status_code == 404
    assert response.json() == {"error": "device_not_found"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/missing-device/dfu/start"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/missing-device/dfu/start"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }


@pytest.mark.device_lab
def test_post_start_dfu_invalid_state_transition():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/device-001/dfu/start", json={"target_version": "2.0.0"})

    assert response.status_code == 409
    assert response.json() == {"error": "invalid_state_transition"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/device-001/dfu/start"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/device-001/dfu/start"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }


@pytest.mark.device_lab
def test_post_start_dfu_unknown_route_returns_404():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/bad_devices/device-001/dfu/start", json={"target_version": "2.0.0"})

    assert response.status_code == 404
    assert response.json() == {"error": "not_found"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/bad_devices/device-001/dfu/start"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/bad_devices/device-001/dfu/start"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }


@pytest.mark.device_lab
def test_post_start_dfu_dfu_already_in_progressError():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")
    inventory.start_dfu("device-001", "2.0.0")
    

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/device-001/dfu/start", json={"target_version": "2.0.0"})

    assert response.status_code == 409
    assert response.json() == {"error": "invalid_state_transition"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/device-001/dfu/start"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/device-001/dfu/start"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }

@pytest.mark.device_lab
def test_post_complete_dfu_returns_online_device():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")
    inventory.start_dfu("device-001", "2.0.0")    
    
    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )
    device = inventory.get("device-001")
    assert isinstance(device, Device)
    assert device.device_id == "device-001"
    assert device.firmware_version == "1.0.0"
    assert device.state == DeviceState.DFU_IN_PROGRESS
    assert device.last_seen_at is not None
    
    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/device-001/dfu/complete", json={"version": "2.0.0"})

    device = inventory.get("device-001")
    assert device.state == DeviceState.ONLINE
    assert device.firmware_version == "2.0.0"

    assert response.status_code == 200
    assert response.json()["device_id"] == "device-001"
    assert response.json()["firmware_version"] == "2.0.0"
    assert response.json()["state"] == "online"
    assert response.json()["last_seen_at"] is not None
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/device-001/dfu/complete"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/device-001/dfu/complete"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }

    
@pytest.mark.device_lab
def test_post_complete_dfu_bad_device():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/missing-device/dfu/complete", json={"version": "2.0.0"})

    assert response.status_code == 404
    assert response.json() == {"error": "device_not_found"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/missing-device/dfu/complete"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/missing-device/dfu/complete"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }


@pytest.mark.device_lab
def test_post_complete_dfu_invalid_state_transition():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/device-001/dfu/complete", json={"version": "2.0.0"})

    assert response.status_code == 409
    assert response.json() == {"error": "invalid_state_transition"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/device-001/dfu/complete"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/device-001/dfu/complete"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }


@pytest.mark.device_lab
def test_post_complete_dfu_unknown_route_returns_404():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/bad_devices/device-001/dfu/complete", json={"version": "2.0.0"})

    assert response.status_code == 404
    assert response.json() == {"error": "not_found"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/bad_devices/device-001/dfu/complete"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/bad_devices/device-001/dfu/complete"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }

@pytest.mark.device_lab
def test_post_fail_dfu_returns_online_device():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")
    inventory.start_dfu("device-001", "2.0.0")    
    
    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )
    device = inventory.get("device-001")
    assert isinstance(device, Device)
    assert device.device_id == "device-001"
    assert device.firmware_version == "1.0.0"
    assert device.state == DeviceState.DFU_IN_PROGRESS
    assert device.last_seen_at is not None
    
    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/device-001/dfu/fail")

    device = inventory.get("device-001")
    assert device.state == DeviceState.ONLINE
    assert device.firmware_version == "1.0.0"

    assert response.status_code == 200
    assert response.json()["device_id"] == "device-001"
    assert response.json()["firmware_version"] == "1.0.0"
    assert response.json()["state"] == "online"
    assert response.json()["last_seen_at"] is not None
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/device-001/dfu/fail"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/device-001/dfu/fail"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }

    
@pytest.mark.device_lab
def test_post_fail_dfu_bad_device():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/missing-device/dfu/fail")

    assert response.status_code == 404
    assert response.json() == {"error": "device_not_found"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/missing-device/dfu/fail"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/missing-device/dfu/fail"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }


@pytest.mark.device_lab
def test_post_fail_dfu_invalid_state_transition():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/device-001/dfu/fail")

    assert response.status_code == 409
    assert response.json() == {"error": "invalid_state_transition"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/devices/device-001/dfu/fail"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/devices/device-001/dfu/fail"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }


@pytest.mark.device_lab
def test_post_fail_dfu_unknown_route_returns_404():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/bad_devices/device-001/dfu/fail")

    assert response.status_code == 404
    assert response.json() == {"error": "not_found"}
    assert "device_id" not in response.json()
    assert response.request.method == "POST"
    assert response.request.url.path == "/bad_devices/device-001/dfu/fail"
    assert response.request.url.host == "device-cloud.test"
    assert str(response.request.url) == "https://device-cloud.test/bad_devices/device-001/dfu/fail"
    assert response.request.url.scheme == "https"
    assert response.request.extensions["timeout"] == {
                                                                "connect": 5.0,
                                                                "read": 5.0,
                                                                "write": 5.0,
                                                                "pool": 5.0,
                                                            }

@pytest.mark.device_lab
def test_set_state_returns_400_when_state_key_is_missing():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
                            base_url="https://device-cloud.test",
                            timeout_s=5.0,
                            log_level="INFO",
                        )

    with ApiClient(settings, transport=transport) as client:
        response = client.post("/devices/device-001/dfu/set_state", json={})

    assert response.status_code == 400

def _api_request(inventory, method, path, **kwargs):
    transport = httpx.MockTransport(create_handler(inventory))
    settings = Settings(
        base_url="https://device-cloud.test",
        timeout_s=5.0,
        log_level="INFO",
    )

    with ApiClient(settings, transport=transport) as client:
        return getattr(client, method.lower())(path, **kwargs)

@pytest.mark.device_lab
def test_set_state_returns_offline_device():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/devices/device-001/dfu/set_state",
        json={"state": "offline"},
    )

    assert response.status_code == 200
    assert response.json()["device_id"] == "device-001"
    assert response.json()["state"] == "offline"
    assert inventory.get("device-001").state == DeviceState.OFFLINE


@pytest.mark.device_lab
def test_set_state_returns_404_when_device_is_missing():
    inventory = InMemoryInventory()

    response = _api_request(
        inventory,
        "POST",
        "/devices/missing-device/dfu/set_state",
        json={"state": "online"},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "device_not_found"}


@pytest.mark.device_lab
@pytest.mark.parametrize("state", ["unknown", "", "   "])
def test_set_state_returns_400_when_state_is_invalid(state):
    inventory = InMemoryInventory()
    inventory.register("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/devices/device-001/dfu/set_state",
        json={"state": state},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "invalid_device_state"}


@pytest.mark.device_lab
def test_set_state_returns_400_when_state_is_not_a_string():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/devices/device-001/dfu/set_state",
        json={"state": 123},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "invalid_device_state"}


@pytest.mark.device_lab
def test_set_state_returns_409_when_transition_is_not_allowed():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/devices/device-001/dfu/set_state",
        json={"state": "offline"},
    )

    assert response.status_code == 409
    assert response.json() == {"error": "invalid_state_transition"}


@pytest.mark.device_lab
def test_set_state_unknown_route_returns_404():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/bad_devices/device-001/dfu/set_state",
        json={"state": "offline"},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "not_found"}

@pytest.mark.device_lab
def test_start_dfu_returns_400_when_json_is_invalid():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/devices/device-001/dfu/start",
        content=b"{",
    )

    assert response.status_code == 400
    assert response.json() == {"error": "invalid_json"}


@pytest.mark.device_lab
def test_start_dfu_returns_400_when_json_is_not_an_object():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/devices/device-001/dfu/start",
        json=["2.0.0"],
    )

    assert response.status_code == 400
    assert response.json() == {"error": "invalid_request_body"}

@pytest.mark.device_lab
def test_start_dfu_returns_400_when_target_version_is_missing():
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/devices/device-001/dfu/start",
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "missing_target_version"}


@pytest.mark.device_lab
@pytest.mark.parametrize("target_version", ["", "   ", 123])
def test_start_dfu_returns_400_when_target_version_is_invalid(target_version):
    inventory = InMemoryInventory()
    inventory.register("device-001")
    inventory.heartbeat("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/devices/device-001/dfu/start",
        json={"target_version": target_version},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "invalid_target_version"}


@pytest.mark.device_lab
def test_complete_dfu_returns_400_when_version_is_missing():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/devices/device-001/dfu/complete",
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "missing_version"}


@pytest.mark.device_lab
@pytest.mark.parametrize("version", ["", "   ", 123])
def test_complete_dfu_returns_400_when_version_is_invalid(version):
    inventory = InMemoryInventory()
    inventory.register("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/devices/device-001/dfu/complete",
        json={"version": version},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "invalid_version"}

@pytest.mark.device_lab
def test_get_device_returns_404_when_path_has_extra_segment():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    response = _api_request(
        inventory,
        "GET",
        "/devices/device-001/extra",
    )

    assert response.status_code == 404
    assert response.json() == {"error": "not_found"}


@pytest.mark.device_lab
def test_heartbeat_returns_404_when_path_has_extra_segment():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    response = _api_request(
        inventory,
        "POST",
        "/devices/device-001/extra/heartbeat",
    )

    assert response.status_code == 404
    assert response.json() == {"error": "not_found"}


@pytest.mark.device_lab
def test_heartbeat_returns_404_when_device_id_is_empty():
    inventory = InMemoryInventory()

    response = _api_request(
        inventory,
        "POST",
        "/devices//heartbeat",
    )

    assert response.status_code == 404
    assert response.json() == {"error": "not_found"}


@pytest.mark.device_lab
def test_get_devices_returns_empty_list_when_inventory_is_empty():
    inventory = InMemoryInventory()

    response = _api_request(inventory, "GET", "/devices")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.device_lab
def test_put_returns_405_when_method_is_not_supported():
    inventory = InMemoryInventory()
    inventory.register("device-001")

    transport = httpx.MockTransport(create_handler(inventory))

    with httpx.Client(
        base_url="https://device-cloud.test",
        transport=transport,
    ) as client:
        response = client.put("/devices/device-001/heartbeat")

    assert response.status_code == 405
    assert response.json() == {"error": "method_not_allowed"}