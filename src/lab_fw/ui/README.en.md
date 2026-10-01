# lab_fw UI

[RU](README.md) · **EN** · [PL](README.pl.md)

UI layer of the framework on **Playwright** (primary). Selenium comes later in phase D.

## Why

Tests should not call raw Playwright in every file: `UIClient` starts Chromium + context/page; page objects (`LoginPage`, `SecurePage`) own locators and actions. Base URL comes from settings/env.

## Install

```bash
pip install -e ".[dev]"
playwright install chromium
```

`playwright` is in optional `dev`. You need the **Chromium binary** (command above), or `BrowserType.launch` fails.

## Settings

| Env | Purpose |
|-----|---------|
| `LAB_FW_UI_BASE_URL` | UI base URL (default `https://the-internet.herokuapp.com`) |

Empty URL → `UiError` when creating `UIClient`.

## UIClient

```python
from lab_fw.ui.client import UIClient
from lab_fw.core.config import get_settings

with UIClient(get_settings()) as ui:
    ui.page.goto("/login")
```

- `start()` / context manager: Playwright → Chromium → context(`base_url=...`) → page  
- `close()` / `__exit__`: tear down page/context/browser/playwright  
- access: `ui.page`, `ui.settings`

Fixtures in `tests/conftest.py`: `ui_client` (function) and `ui_client_module` (module, shared session).

## Page objects

| Class | path | Idea |
|-------|------|------|
| `LoginPage` | `/login` | fields, login → returns `SecurePage` |
| `SecurePage` | `/secure` | logout → returns `LoginPage` |

Both extend `lab_fw.abstractions.BasePage` (`open`, `path`). Waits use Playwright auto-wait / locators — no `time.sleep`.

Demo site: [the-internet.herokuapp.com](https://the-internet.herokuapp.com/) (login / secure).

## Run

```bash
pytest -m ui -q
pytest -q
```

Marker `ui` is registered in `pyproject.toml`.

URL asserts build from `settings.ui_base_url`, not a hardcoded host.

Some module-scoped tests **intentionally** share one `page` (documented in the test docstring); running such a test alone may fail.

## Why Playwright primary

Stable auto-waits, one Chromium API, convenient sync Python API. Selenium will appear as D2 (second stack), not as a replacement.
