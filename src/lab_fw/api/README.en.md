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

## Tests

```bash
pytest -q tests/test_api_auth.py
pytest -q -m api
```
