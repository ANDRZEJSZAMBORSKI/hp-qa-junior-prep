# lab_fw API

**RU** · [EN](README.en.md) · [PL](README.pl.md)

<!-- mod-preamble -->

### О модуле API

Пакет `lab_fw.api` — HTTP-клиент с явной политикой ошибок, optional Bearer, pydantic-схемами и **opt-in** retry. Документ связан с корневым README **I1–I3** и [mocks_lab](../../../tests/mocks_lab/README.md).

**Файлы:** `client.py`, `auth.py`, `schemas.py`, `retry_policy.py`.

## Установка

<!-- mod-deep:api:install -->
### О разделе — установка

Editable install подтягивает `httpx`, `pydantic` (dev). Без `[dev]` часть тестов недоступна.

## Settings / token

<!-- mod-deep:api:settings -->
### О разделе — Settings

`get_settings()` читает env один раз за процесс; см. корневой README «Переменные окружения». Token опционален — многие тесты используют MockTransport без Bearer.

## Bearer

<!-- mod-deep:api:bearer -->
### О разделе — Bearer

Заголовок ставится при создании клиента, если `api_token` задан. Обновление токена после OAuth — `set_bearer_token`.

## Client credentials (mock-flow)

<!-- mod-deep:api:oauth -->
### О разделе — client credentials

Демо OAuth без IdP: `fetch_client_credentials_token` → POST `/oauth/token` через тот же `ApiClient` (мокается transport).

**Проверка:** `pytest tests/test_api_auth.py -q`

## Schema (pydantic)

<!-- mod-deep:api:schema -->
### О разделе — Schema

`parse_user` / `parse_token` централизуют валидацию JSON → `SchemaError` вместо KeyError в каждом тесте.

**Проверка:** `pytest tests/test_api_schemas.py -q`

## Negative / errors

<!-- mod-deep:api:negative -->
### О разделе — Negative / errors

4xx/5xx **не** exception по умолчанию — явный контракт. Transport → `ApiError` с `__cause__`.

**Проверка:** `pytest tests/test_api_negative.py tests/test_compose_api.py -q`

## Retry policy

<!-- mod-deep:api:retry -->
### О разделе — Retry policy

Retry только через `retry_call`, не внутри каждого `get`. Таблица ниже — источник истины для L1 п.3 и L2 worker.

**Проверка:** `pytest tests/test_api_retry_policy.py -q`

## Тесты

<!-- mod-deep:api:tests -->
### О разделе — тесты API

Запускай по файлам при локализации регрессии; `-m api` — весь маркированный набор.

