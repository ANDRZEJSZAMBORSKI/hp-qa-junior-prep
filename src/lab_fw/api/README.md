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

## Тесты

```bash
pytest -q tests/test_api_auth.py
pytest -q tests/test_api_schemas.py
pytest -q -m api
```
