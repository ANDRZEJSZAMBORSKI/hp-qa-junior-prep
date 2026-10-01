# lab_fw UI

[RU](README.md) · **EN** · [PL](README.pl.md)

UI layer: **Playwright = primary**, **Selenium = second stack** (D2). Do not mix stacks in one page class.

## Why

Tests should not call raw browser APIs in every file: a client owns browser/driver lifecycle; page objects own locators and actions. Base URL comes from settings/env.

## Install

```bash
pip install -e ".[dev]"
playwright install chromium
```

`dev` includes `playwright` and `selenium`. Playwright needs the Chromium binary (command above). Selenium 4 uses **Selenium Manager** (manual chromedriver usually not required).

## Settings

| Env | Purpose |
|-----|---------|
| `LAB_FW_UI_BASE_URL` | UI base URL (default `https://the-internet.herokuapp.com`) |

Empty URL → `UiError` when creating a client.

Demo: [the-internet.herokuapp.com](https://the-internet.herokuapp.com/) (login / secure).

---

## Playwright (primary) — `UIClient`

```python
from lab_fw.ui.client import UIClient
from lab_fw.core.config import get_settings

with UIClient(get_settings()) as ui:
    ui.page.goto("/login")
```

- `start()` / CM: Playwright → Chromium → context(`base_url=...`) → page  
- pages: `lab_fw.ui.pages` (`LoginPage`, `SecurePage`)  
- fixtures: `ui_client`, `ui_client_module`  
- marker: `@pytest.mark.ui`  
- waits: Playwright auto-wait, no `time.sleep`

```bash
pytest -m ui -q
```

---

## Selenium (D2) — `SeleniumClient`

Separate lifecycle and pages: `lab_fw.ui.selenium_client`, `lab_fw.ui.selenium_pages`.

```python
from lab_fw.ui.selenium_client import SeleniumClient
from lab_fw.ui.selenium_pages.login_page import LoginPage
from lab_fw.core.config import get_settings

with SeleniumClient(get_settings()) as sc:
    page = LoginPage(sc.driver, settings.ui_base_url)
    page.open()
```

- Chrome + **Selenium Manager**  
- Chrome options disable Password Manager / leak detection (otherwise a second login with the demo password can show “Change password” and break typing)  
- pages on `BasePage`; prefer **ID** locators (`#username`, `#password`)  
- waits: `WebDriverWait` + `expected_conditions` (explicit), no `time.sleep`  
- failed login/logout navigation → `UiError` (do not mask with `return self`)  
- fixtures: `selenium_client`, `selenium_client_module`  
- marker: `@pytest.mark.selenium`

```bash
pytest -m selenium -q
```

| | Playwright | Selenium |
|--|------------|----------|
| Client | `UIClient` | `SeleniumClient` |
| Pages | `ui.pages` | `ui.selenium_pages` |
| Marker | `ui` | `selenium` |
| Wait | auto-wait | explicit `WebDriverWait` |

---

## Full run

```bash
pytest -m ui -q
pytest -m selenium -q
pytest -q
```

URL asserts use `settings.ui_base_url`, not a hardcoded host.

Some module-scoped tests **intentionally** share one session (documented in docstrings); running such a test alone may fail.

## Why Playwright primary

Stable auto-waits and a convenient sync API. Selenium is the second stack for HP’s “Selenium / Playwright” expectation — know both, without cloning the entire suite one-to-one.
