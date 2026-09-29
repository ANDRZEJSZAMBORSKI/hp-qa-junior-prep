# lab_fw API

[RU](README.md) · **EN** · [PL](README.pl.md)

HTTP client `ApiClient` and a training auth layer.

## Install

```bash
pip install -e ".[dev]"
```

## Settings / token

| Env | Purpose |
|-----|---------|
| `LAB_FW_BASE_URL` | base URL (default `https://example.com`) |
| `LAB_FW_TIMEOUT_S` | timeout in seconds |
| `LAB_FW_LOG_LEVEL` | log level |
| `LAB_FW_API_TOKEN` | optional Bearer (if set → sent as `Authorization`) |

With no `LAB_FW_API_TOKEN`, the header is not set.

## Bearer

On client create, if settings have `api_token`:

```text
Authorization: Bearer <token>
```

After OAuth you can refresh:

```python
client.set_bearer_token("tok-123")
```

## Client credentials (mock flow)

```python
from lab_fw.api.auth import fetch_client_credentials_token

token = fetch_client_credentials_token(client, "client-id", "client-secret")
# POST /oauth/token (form) → access_token → set_bearer_token
```

HTTP ≥400 / invalid JSON / missing `access_token` → `ApiError`.

In unit tests the endpoint is mocked with `httpx.MockTransport` — no real IdP.

## Schema (pydantic)

API responses are validated via models in `lab_fw.api.schemas` (not ad-hoc field asserts in every test).

| Model | Fields | Policy |
|-------|--------|--------|
| `User` | `id: int`, `name: str` | `strict=True`, `extra="forbid"` |
| `TokenResponse` | `access_token`, `token_type`, `expires_in` | same |

```python
from lab_fw.api.schemas import parse_user, parse_token

user = parse_user(response.json())
token = parse_token(response.json())
```

Validation failure → `SchemaError` (subclass of `ApiError`).  
`pydantic>=2` is in optional `dev`.

## Negative / errors

`ApiClient.get/post` do **not** raise on 4xx/5xx by themselves — they return `httpx.Response`.  
Check status explicitly:

```python
from lab_fw.api.client import ensure_success

response = client.get("/users/999")
ensure_success(response)  # status < 400 → same response; else HttpStatusError
```

| Type | When |
|------|------|
| `HttpStatusError` (`ApiError`) | `ensure_success` when status ≥ 400 (Allure attach: status/body) |
| `ApiError` | transport: `ConnectError`, `ReadTimeout`, … |
| `SchemaError` (`ApiError`) | 200 OK, but JSON fails the schema |

Hierarchy:

```text
ApiError
 ├── SchemaError
 └── HttpStatusError
```

## Retry policy

Retry is **not** built into every `get/post`. Call it explicitly:

```python
from lab_fw.core.retry import retry_call
from lab_fw.api.client import ensure_success

def once():
    return ensure_success(client.get("/users"))

retry_call(once, delay_s=0, retry_on=(ApiError,), retry_if=True)
```

`retry_if=True` → decision via `lab_fw.api.retry_policy.should_retry`.

| Situation | Retry? |
|-----------|--------|
| GET + HTTP **429** / **503** (`HttpStatusError`) | yes |
| GET + transport (`ConnectError` / `ReadTimeout` → `ApiError`) | yes |
| GET + **400 / 401 / 403 / 404 / 422 / 500** | no |
| POST / non-GET | no |
| non-`ApiError` | no (re-raised when `retry_if=True`) |

`HttpStatusError` keeps `response` so the policy can see method/status.

## Tests

```bash
pytest -q tests/test_api_auth.py
pytest -q tests/test_api_schemas.py
pytest -q tests/test_api_negative.py
pytest -q tests/test_api_retry_policy.py
pytest -q -m api
```
