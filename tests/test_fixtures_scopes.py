import httpx
import pytest

@pytest.mark.smoke
@pytest.mark.api
def test_api_client_get(api_client):
    response = api_client.get("/users")

    assert response.status_code == 200
    assert response.json() == {"ok": True}

@pytest.mark.smoke
@pytest.mark.api
def test_module_settings_first(module_settings, module_settings_id):
    assert id(module_settings) == module_settings_id
    print(f"module_settings id: {id(module_settings)}")
    print(f"id(module_settings): {id(module_settings)}")

@pytest.mark.smoke
@pytest.mark.api
def test_module_settings_second(module_settings, module_settings_id):
    assert id(module_settings) == module_settings_id
    print(f"module_settings id: {id(module_settings)}")
    print(f"id(module_settings): {id(module_settings)}")
