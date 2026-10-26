# Mocks lab

[RU](README.md) · **EN** · [PL](README.pl.md)

Module: **pure mocks** (`unittest.mock`, `patch`, spy, `monkeypatch`) and **`httpx.MockTransport`** on our `ApiClient` / `Settings` / `ApiError` / `retry_call` / logging / pytest.

Shows dependency substitution at two levels: Python object/method mocks and `httpx` transport on `ApiClient`.

---

## How to run

<!-- mod-deep:mocks_lab:run -->
#### About this section — running

Filters `mocks_pure` / `mocks_httpx` split Part I and II without listing files by hand.

## Layout

<!-- mod-deep:mocks_lab:structure -->
#### About this section — layout

Two transport files intentionally duplicate ideas — compare fixture vs manual Settings.

## Part I — pure mocks

<!-- mod-deep:mocks_lab:pure -->
#### About this section — pure mocks

Patching at the wrong layer is a common junior mistake. Ask: are we replacing the **client**, a **method**, or the **transport**?

## Part II — `httpx.MockTransport`

<!-- mod-deep:mocks_lab:transport -->
#### About this section — MockTransport

Preferred style for `ApiClient(settings, transport=...)`. The handler sees a real `httpx.Request`.

## When to use what (cheat sheet)

<!-- mod-deep:mocks_lab:cheatsheet -->
#### About this section — cheat sheet

Use the table in code review: transport for HTTP contract, mock for a narrow logic branch.

## Tie-in with `lab_fw`

<!-- mod-deep:mocks_lab:tiein -->
#### About this section — tie-in with lab_fw

Retry logs are already in conftest — look for WARNING with `pytest -v tests/mocks_lab`.

