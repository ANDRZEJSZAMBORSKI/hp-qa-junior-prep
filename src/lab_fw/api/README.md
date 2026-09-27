# lab_fw API

**RU** · [EN](README.en.md) · [PL](README.pl.md)

HTTP-клиент `ApiClient` и учебный auth-слой.

## Установка

```bash
pip install -e ".[dev]"
```

## Settings / token

| Env | Назначение |
|-----|------------|
| `LAB_FW_BASE_URL` | base URL (default `https://example.com`) |
| `LAB_FW_TIMEOUT_S` | timeout секунд |
| `LAB_FW_LOG_LEVEL` | уровень логов |
| `LAB_FW_API_TOKEN` | optional Bearer (если задан — уходит в `Authorization`) |

Без `LAB_FW_API_TOKEN` заголовок не ставится.

## Bearer

При создании клиента, если в settings есть `api_token`:

```text
Authorization: Bearer <token>
```

После OAuth можно обновить:

```python
client.set_bearer_token("tok-123")
```

## Client credentials (mock-flow)

```python
from lab_fw.api.auth import fetch_client_credentials_token

token = fetch_client_credentials_token(client, "client-id", "client-secret")
# POST /oauth/token (form) → access_token → set_bearer_token
```

Ошибки HTTP ≥400 / битый JSON / нет `access_token` → `ApiError`.

В unit-тестах endpoint мокается через `httpx.MockTransport`, без реального IdP.

## Тесты

```bash
pytest -q tests/test_api_auth.py
pytest -q -m api
```
