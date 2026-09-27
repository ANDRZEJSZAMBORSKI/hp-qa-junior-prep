# lab_fw API

[RU](README.md) · [EN](README.en.md) · **PL**

Klient HTTP `ApiClient` i szkoleniowa warstwa auth.

## Instalacja

```bash
pip install -e ".[dev]"
```

## Settings / token

| Env | Znaczenie |
|-----|-----------|
| `LAB_FW_BASE_URL` | base URL (domyślnie `https://example.com`) |
| `LAB_FW_TIMEOUT_S` | timeout w sekundach |
| `LAB_FW_LOG_LEVEL` | poziom logów |
| `LAB_FW_API_TOKEN` | opcjonalny Bearer (jeśli ustawiony → `Authorization`) |

Bez `LAB_FW_API_TOKEN` nagłówek nie jest ustawiany.

## Bearer

Przy tworzeniu klienta, jeśli w settings jest `api_token`:

```text
Authorization: Bearer <token>
```

Po OAuth można odświeżyć:

```python
client.set_bearer_token("tok-123")
```

## Client credentials (mock-flow)

```python
from lab_fw.api.auth import fetch_client_credentials_token

token = fetch_client_credentials_token(client, "client-id", "client-secret")
# POST /oauth/token (form) → access_token → set_bearer_token
```

HTTP ≥400 / zły JSON / brak `access_token` → `ApiError`.

W unit-testach endpoint mockujemy przez `httpx.MockTransport`, bez prawdziwego IdP.

## Testy

```bash
pytest -q tests/test_api_auth.py
pytest -q -m api
```
