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

## Schema (pydantic)

Odpowiedzi API walidujemy modelami w `lab_fw.api.schemas` (nie ręcznymi assertami pól w każdym teście).

| Model | Pola | Polityka |
|-------|------|----------|
| `User` | `id: int`, `name: str` | `strict=True`, `extra="forbid"` |
| `TokenResponse` | `access_token`, `token_type`, `expires_in` | to samo |

```python
from lab_fw.api.schemas import parse_user, parse_token

user = parse_user(response.json())
token = parse_token(response.json())
```

Błąd walidacji → `SchemaError` (dziedziczy po `ApiError`).  
`pydantic>=2` jest w optional `dev`.

## Negative / errors

`ApiClient.get/post` **nie** rzucają przy 4xx/5xx — zwracają `httpx.Response`.  
Status sprawdzaj jawnie:

```python
from lab_fw.api.client import ensure_success

response = client.get("/users/999")
ensure_success(response)  # status < 400 → ten sam response; inaczej HttpStatusError
```

| Typ | Kiedy |
|-----|--------|
| `HttpStatusError` (`ApiError`) | `ensure_success` przy status ≥ 400 (Allure attach: status/body) |
| `ApiError` | transport: `ConnectError`, `ReadTimeout`, … |
| `SchemaError` (`ApiError`) | 200 OK, ale JSON nie przechodzi schematu |

Hierarchia:

```text
ApiError
 ├── SchemaError
 └── HttpStatusError
```

## Retry policy

Retry **nie** jest włączony w każdy `get/post`. Wywołuj jawnie:

```python
from lab_fw.core.retry import retry_call
from lab_fw.api.client import ensure_success

def once():
    return ensure_success(client.get("/users"))

retry_call(once, delay_s=0, retry_on=(ApiError,), retry_if=True)
```

`retry_if=True` → decyzja przez `lab_fw.api.retry_policy.should_retry`.

| Sytuacja | Retry? |
|----------|--------|
| GET + HTTP **429** / **503** (`HttpStatusError`) | tak |
| GET + transport (`ConnectError` / `ReadTimeout` → `ApiError`) | tak |
| GET + **400 / 401 / 403 / 404 / 422 / 500** | nie |
| POST / nie-GET | nie |
| nie-`ApiError` | nie (przy `retry_if=True` propagowane) |

`HttpStatusError` trzyma `response`, żeby policy widziała method/status.

## Testy

```bash
pytest -q tests/test_api_auth.py
pytest -q tests/test_api_schemas.py
pytest -q tests/test_api_negative.py
pytest -q tests/test_api_retry_policy.py
pytest -q -m api
```
