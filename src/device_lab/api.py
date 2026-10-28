import json

import httpx
from device_lab.models import DeviceState
from device_lab.inventory import InMemoryInventory
from lab_fw.core.errors import (
    DeviceNotFoundError,
    DfuAlreadyInProgressError,
    InvalidStateTransitionError,
)

def get_device_id(request: httpx.Request, path: str, start: str, end: list[str]) -> str | httpx.Response:
    parts = path.strip("/").split("/")

    if len(parts) != 2 + len(end):
        return _error_response(request, 404, "not_found")

    if parts[0] != start or parts[2:] != end:
        return _error_response(request, 404, "not_found")

    device_id = parts[1]

    if not device_id.strip():
        return _error_response(request, 404, "not_found")
    return device_id

def _error_response(
    request: httpx.Request,
    status_code: int,
    error: str,
) -> httpx.Response:
    return httpx.Response(
        status_code,
        json={"error": error},
        request=request,
    )

def _read_json_object(
    request: httpx.Request,
) -> dict[str, object] | httpx.Response:
    try:
        body = json.loads(request.content)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _error_response(request, 400, "invalid_json")

    if not isinstance(body, dict):
        return _error_response(request, 400, "invalid_request_body")

    return body

def _required_string(
    request: httpx.Request,
    body: dict[str, object],
    key: str,
    missing_error: str,
    invalid_error: str,
) -> str | httpx.Response:
    if key not in body:
        return _error_response(request, 400, missing_error)

    value = body[key]

    if not isinstance(value, str) or not value.strip():
        return _error_response(request, 400, invalid_error)

    return value

def create_handler(inventory: InMemoryInventory):
    def handle_request(request: httpx.Request) -> httpx.Response:
        method = request.method
        path = request.url.path
        
        if method == "GET" and path == "/devices":
            devices = inventory.list_devices()

            return httpx.Response(
                200,
                json=[device.model_dump(mode="json") for device in devices],
                request=request,
            )
        if method == "GET" and path.startswith("/devices/"):
            device_id = get_device_id(request, path, "devices", [])
            if isinstance(device_id, httpx.Response):
                return device_id
            
            try:
                device = inventory.get(device_id)
            except DeviceNotFoundError:
                return _error_response(request, 404, "device_not_found")
            
            return httpx.Response(
                200,
                json=device.model_dump(mode="json"),
                request=request,
            )

        if method == "POST" and path.startswith("/devices/") and path.endswith("/heartbeat"):
            
            device_id = get_device_id(request, path, "devices", ["heartbeat"])
            if isinstance(device_id, httpx.Response):
                return device_id
            try:
                device = inventory.heartbeat(device_id)
            except DeviceNotFoundError:
                return _error_response(request, 404, "device_not_found")

            return httpx.Response(
                200,
                json=device.model_dump(mode="json"),
                request=request,
            )

        if method == "POST" and path.startswith("/devices/") and path.endswith("/dfu/start"):
            device_id = get_device_id(request, path, "devices", ["dfu","start"])
            if isinstance(device_id, httpx.Response):
                return device_id            
            body = _read_json_object(request)
            if isinstance(body, httpx.Response):
                return body
            target_version = _required_string(
                request,
                body,
                "target_version",
                "missing_target_version",
                "invalid_target_version",
            )
            if isinstance(target_version, httpx.Response):
                return target_version

            try:
                device = inventory.start_dfu(device_id, target_version)
            except DeviceNotFoundError:
                return _error_response(request, 404, "device_not_found")
            except (InvalidStateTransitionError, DfuAlreadyInProgressError):
                return _error_response(request, 409, "invalid_state_transition")

            return httpx.Response(
                200,
                json=device.model_dump(mode="json"),
                request=request,
            )

        if method == "POST" and path.startswith("/devices/") and path.endswith("/dfu/complete"):
            device_id = get_device_id(request, path, "devices", ["dfu", "complete"])
            if isinstance(device_id, httpx.Response):
                return device_id
            body = _read_json_object(request)
            if isinstance(body, httpx.Response):
                return body

            version = _required_string(
                request,
                body,
                "version",
                "missing_version",
                "invalid_version",
            )
            if isinstance(version, httpx.Response):
                return version
            
            try:
                device = inventory.complete_dfu(device_id, version)
            except DeviceNotFoundError:
                return _error_response(request, 404, "device_not_found")
            except InvalidStateTransitionError:
                return _error_response(request, 409, "invalid_state_transition")

            return httpx.Response(
                200,
                json=device.model_dump(mode="json"),
                request=request,
            )

        if method == "POST" and path.startswith("/devices/") and path.endswith("/dfu/fail"):
            device_id = get_device_id(request, path, "devices", ["dfu", "fail"])
            if isinstance(device_id, httpx.Response):
                return device_id
            try:
                device = inventory.fail_dfu(device_id)
            except DeviceNotFoundError:
                return _error_response(request, 404, "device_not_found")
            except InvalidStateTransitionError:
                return _error_response(request, 409, "invalid_state_transition")

            return httpx.Response(
                200,
                json=device.model_dump(mode="json"),
                request=request,
            )

        if method == "POST" and path.startswith("/devices/") and path.endswith("/dfu/set_state"):
            device_id = get_device_id(request, path, "devices", ["dfu","set_state"])
            if isinstance(device_id, httpx.Response):
                return device_id
            body = _read_json_object(request)
            if isinstance(body, httpx.Response):
                return body

            state_value = _required_string(
                request,
                body,
                "state",
                "missing_state",
                "invalid_device_state",
            )
            if isinstance(state_value, httpx.Response):
                return state_value

            try:
                state = DeviceState(state_value)
            except ValueError:
                return _error_response(request, 400, "invalid_device_state")
            
            try:
                device = inventory.set_state(device_id, state)       
            except DeviceNotFoundError:
                return _error_response(request, 404, "device_not_found")
            except InvalidStateTransitionError:
                return _error_response(request, 409, "invalid_state_transition")
            
            return httpx.Response(
                200,
                json=device.model_dump(mode="json"),
                request=request,
            )

        if path.startswith("/devices/"):
            return _error_response(request, 405, "method_not_allowed")
        
        return _error_response(request, 404, "not_found")

    return handle_request