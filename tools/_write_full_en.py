#!/usr/bin/env python3
"""Write complete English module deep-block sources (UTF-8)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent

MODULES: dict[str, dict[str, str]] = {
    "api": {
        "00_preamble": """### About the API module

The `lab_fw.api` package is an HTTP client with explicit error handling, optional Bearer auth, pydantic schemas, and **opt-in** retry. This guide ties to root README **I1–I3** and [mocks_lab](../../../tests/mocks_lab/README.en.md).

**Files:** `client.py`, `auth.py`, `schemas.py`, `retry_policy.py`.""",
        "install": """#### About this section — install

Editable install pulls in `httpx` and `pydantic` (dev). Without `[dev]`, part of the test suite is unavailable.""",
        "settings": """#### About this section — Settings

`get_settings()` reads env once per process; see root README “Environment variables”. Token is optional — many tests use MockTransport without Bearer.""",
        "bearer": """#### About this section — Bearer

The header is set when the client is created if `api_token` is present. Refresh after OAuth via `set_bearer_token`.""",
        "oauth": """#### About this section — client credentials

Demo OAuth without an IdP: `fetch_client_credentials_token` → POST `/oauth/token` through the same `ApiClient` (mocked transport).

**Check:** `pytest tests/test_api_auth.py -q`""",
        "schema": """#### About this section — Schema

`parse_user` / `parse_token` centralize JSON validation → `SchemaError` instead of KeyError in every test.

**Check:** `pytest tests/test_api_schemas.py -q`""",
        "negative": """#### About this section — Negative / errors

4xx/5xx are **not** exceptions by default — explicit contract. Transport failures → `ApiError` with `__cause__`.

**Check:** `pytest tests/test_api_negative.py tests/test_compose_api.py -q`""",
        "retry": """#### About this section — Retry policy

Retry only through `retry_call`, not inside every `get`. The table below is the source of truth for L1 item 3 and the L2 worker.

**Check:** `pytest tests/test_api_retry_policy.py -q`""",
        "tests": """#### About this section — API tests

Run by file when isolating regressions; `-m api` runs the full marked set.""",
    },
    "reporting": {
        "00_preamble": """### About the reporting module

Allure facade: tests do not import `allure` directly — easier no-op without `allure-pytest` and one style for steps/attachments. See root **N1–N2**.""",
        "install": """#### About this section — install

`allure-pytest` is in `[dev]`. Without it, decorators and steps are no-ops.""",
        "api": """#### About this section — reporting API

Decorators via `decor_allure`: epic/feature/severity/testcase/issue. `ApiClient` already emits steps on HTTP.""",
        "n1": """#### About this section — N1 metadata

`categories.json` plus dynamic `environment.properties` in `tests/conftest.py` (master process only).""",
        "n2": """#### About this section — N2

Links in Allure ≠ upload to TestRail (trcli). Both are described in root README N2.""",
        "run": """#### About this section — running

`--alluredir` is required for result files; `allure serve` is local-only.""",
        "tests": """#### About this section — layer tests

`pytest -m reporting` does not collect the name `testcase` as a test (`python_functions = test_*` in pyproject).""",
    },
    "mocks_lab": {
        "00_preamble": """### About mocks_lab

**Pattern catalog** for dependency substitution: from `unittest.mock` to `httpx.MockTransport`. Linked to **I2** and [API README](../../../src/lab_fw/api/README.en.md).""",
        "run": """#### About this section — running

Filters `mocks_pure` / `mocks_httpx` split Part I and II without listing files by hand.""",
        "structure": """#### About this section — layout

Two transport files intentionally duplicate ideas — compare fixture vs manual Settings.""",
        "pure": """#### About this section — pure mocks

Patching at the wrong layer is a common junior mistake. Ask: are we replacing the **client**, a **method**, or the **transport**?""",
        "transport": """#### About this section — MockTransport

Preferred style for `ApiClient(settings, transport=...)`. The handler sees a real `httpx.Request`.""",
        "cheatsheet": """#### About this section — cheat sheet

Use the table in code review: transport for HTTP contract, mock for a narrow logic branch.""",
        "tiein": """#### About this section — tie-in with lab_fw

Retry logs are already in conftest — look for WARNING with `pytest -v tests/mocks_lab`.""",
    },
}


def main() -> None:
    mod_root = ROOT / "module_deep_blocks"
    for module, files in MODULES.items():
        en_dir = mod_root / module / "en"
        en_dir.mkdir(parents=True, exist_ok=True)
        for key, text in files.items():
            (en_dir / f"{key}.md").write_text(text.strip() + "\n", encoding="utf-8")
        print(f"Wrote {len(files)} EN blocks for {module}")


if __name__ == "__main__":
    main()
