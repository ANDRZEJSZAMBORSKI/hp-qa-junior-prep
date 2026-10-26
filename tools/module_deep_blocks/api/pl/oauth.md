#### O sekcji — client credentials

Demo OAuth bez IdP: `fetch_client_credentials_token` → POST `/oauth/token` przez ten sam `ApiClient` (mockowany transport).

**Sprawdzenie:** `pytest tests/test_api_auth.py -q`
