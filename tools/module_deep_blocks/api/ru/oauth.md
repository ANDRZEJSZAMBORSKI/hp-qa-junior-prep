### О разделе — client credentials

Демо OAuth без IdP: `fetch_client_credentials_token` → POST `/oauth/token` через тот же `ApiClient` (мокается transport).

**Проверка:** `pytest tests/test_api_auth.py -q`
