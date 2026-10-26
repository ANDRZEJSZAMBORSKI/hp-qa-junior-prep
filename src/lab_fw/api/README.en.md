# lab_fw API

[RU](README.md) · **EN** · [PL](README.pl.md)

<!-- mod-preamble -->

### About the API module

The `lab_fw.api` package is an HTTP client with explicit error handling, optional Bearer auth, pydantic schemas, and **opt-in** retry. This guide ties to root README **I1–I3** and [mocks_lab](../../../tests/mocks_lab/README.en.md).

**Files:** `client.py`, `auth.py`, `schemas.py`, `retry_policy.py`.

## Install

<!-- mod-deep:api:install -->
#### About this section — install

Editable install pulls in `httpx` and `pydantic` (dev). Without `[dev]`, part of the test suite is unavailable.

## Settings / token

<!-- mod-deep:api:settings -->
#### About this section — Settings

`get_settings()` reads env once per process; see root README “Environment variables”. Token is optional — many tests use MockTransport without Bearer.

## Bearer

<!-- mod-deep:api:bearer -->
#### About this section — Bearer

The header is set when the client is created if `api_token` is present. Refresh after OAuth via `set_bearer_token`.

## Client credentials (mock flow)

<!-- mod-deep:api:oauth -->
#### About this section — client credentials

Demo OAuth without an IdP: `fetch_client_credentials_token` → POST `/oauth/token` through the same `ApiClient` (mocked transport).

**Check:** `pytest tests/test_api_auth.py -q`

## Schema (pydantic)

<!-- mod-deep:api:schema -->
#### About this section — Schema

`parse_user` / `parse_token` centralize JSON validation → `SchemaError` instead of KeyError in every test.

**Check:** `pytest tests/test_api_schemas.py -q`

## Negative / errors

<!-- mod-deep:api:negative -->
#### About this section — Negative / errors

4xx/5xx are **not** exceptions by default — explicit contract. Transport failures → `ApiError` with `__cause__`.

**Check:** `pytest tests/test_api_negative.py tests/test_compose_api.py -q`

## Retry policy

<!-- mod-deep:api:retry -->
#### About this section — Retry policy

Retry only through `retry_call`, not inside every `get`. The table below is the source of truth for L1 item 3 and the L2 worker.

**Check:** `pytest tests/test_api_retry_policy.py -q`

## Tests

<!-- mod-deep:api:tests -->
#### About this section — API tests

Run by file when isolating regressions; `-m api` runs the full marked set.

