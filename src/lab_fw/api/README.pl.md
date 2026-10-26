# lab_fw API

[RU](README.md) · [EN](README.en.md) · **PL**

<!-- mod-preamble -->

### O module API

Pakiet `lab_fw.api` — klient HTTP z jawną polityką błędów, opcjonalnym Bearer, schematami pydantic i retry **opt-in**. Dokument powiązany z README głównym **I1–I3** oraz [mocks_lab](../../../tests/mocks_lab/README.pl.md).

**Pliki:** `client.py`, `auth.py`, `schemas.py`, `retry_policy.py`.

## Instalacja

<!-- mod-deep:api:install -->
#### O sekcji — instalacja

Instalacja editable dołącza `httpx`, `pydantic` (dev). Bez `[dev]` część testów jest niedostępna.

## Settings / token

<!-- mod-deep:api:settings -->
#### O sekcji — Settings

`get_settings()` czyta env raz na proces; zob. README główne „Zmienne środowiskowe”. Token jest opcjonalny — wiele testów używa MockTransport bez Bearer.

## Bearer

<!-- mod-deep:api:bearer -->
#### O sekcji — Bearer

Nagłówek ustawiany przy tworzeniu klienta, gdy `api_token` jest podany. Odświeżenie tokenu po OAuth — `set_bearer_token`.

## Client credentials (mock-flow)

<!-- mod-deep:api:oauth -->
#### O sekcji — client credentials

Demo OAuth bez IdP: `fetch_client_credentials_token` → POST `/oauth/token` przez ten sam `ApiClient` (mockowany transport).

**Sprawdzenie:** `pytest tests/test_api_auth.py -q`

## Schema (pydantic)

<!-- mod-deep:api:schema -->
#### O sekcji — Schema

`parse_user` / `parse_token` centralizują walidację JSON → `SchemaError` zamiast KeyError w każdym teście.

**Sprawdzenie:** `pytest tests/test_api_schemas.py -q`

## Negative / errors

<!-- mod-deep:api:negative -->
#### O sekcji — Negative / errors

4xx/5xx **domyślnie nie** rzucają wyjątku — jawny kontrakt. Transport → `ApiError` z `__cause__`.

**Sprawdzenie:** `pytest tests/test_api_negative.py tests/test_compose_api.py -q`

## Retry policy

<!-- mod-deep:api:retry -->
#### O sekcji — Retry policy

Retry tylko przez `retry_call`, nie wewnątrz każdego `get`. Tabela poniżej to źródło prawdy dla L1 pkt 3 i workera L2.

**Sprawdzenie:** `pytest tests/test_api_retry_policy.py -q`

## Testy

<!-- mod-deep:api:tests -->
#### O sekcji — testy API

Uruchamiaj plikami przy lokalizacji regresji; `-m api` — cały zestaw z markerem.

