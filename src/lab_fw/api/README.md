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

## Schema (pydantic)

Ответы API валидируются через модели в `lab_fw.api.schemas` (не сырой `allure`/`assert` по полям вручную в каждом тесте).

| Модель | Поля | Политика |
|--------|------|----------|
| `User` | `id: int`, `name: str` | `strict=True`, `extra="forbid"` |
| `TokenResponse` | `access_token`, `token_type`, `expires_in` | то же |

```python
from lab_fw.api.schemas import parse_user, parse_token

user = parse_user(response.json())
token = parse_token(response.json())
```

Ошибка валидации → `SchemaError` (наследник `ApiError`).  
`pydantic>=2` — в optional `dev`.

## Negative / errors

`ApiClient.get/post` **не** кидают на 4xx/5xx сами — возвращают `httpx.Response`.  
Проверка статуса — явно:

```python
from lab_fw.api.client import ensure_success

response = client.get("/users/999")
ensure_success(response)  # status < 400 → тот же response; иначе HttpStatusError
```

| Тип | Когда |
|-----|--------|
| `HttpStatusError` (`ApiError`) | `ensure_success` при status ≥ 400 (в Allure — attach status/body) |
| `ApiError` | transport: `ConnectError`, `ReadTimeout`, … |
| `SchemaError` (`ApiError`) | 200 OK, но JSON не проходит схему |

Иерархия:

```text
ApiError
 ├── SchemaError
 └── HttpStatusError
```

## Retry policy

Retry **не** включён в каждый `get/post`. Явно:

```python
from lab_fw.core.retry import retry_call
from lab_fw.api.client import ensure_success

def once():
    return ensure_success(client.get("/users"))

retry_call(once, delay_s=0, retry_on=(ApiError,), retry_if=True)
```

`retry_if=True` → решение через `lab_fw.api.retry_policy.should_retry`.

| Ситуация | Retry? |
|----------|--------|
| GET + HTTP **429** / **503** (`HttpStatusError`) | да |
| GET + transport (`ConnectError` / `ReadTimeout` → `ApiError`) | да |
| GET + **400 / 401 / 403 / 404 / 422 / 500** | нет |
| POST / не-GET | нет |
| не-`ApiError` | нет (при `retry_if=True` пробрасывается) |

`HttpStatusError` хранит `response`, чтобы policy видела method/status.

## Тесты

```bash
pytest -q tests/test_api_auth.py
pytest -q tests/test_api_schemas.py
pytest -q tests/test_api_negative.py
pytest -q tests/test_api_retry_policy.py
pytest -q -m api
```
