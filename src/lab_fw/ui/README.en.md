# lab_fw UI

[RU](README.md) · **EN** · [PL](README.pl.md)

UI layer: **Playwright = primary**, **Selenium = second stack** (D2). Do not mix stacks in one page class.

Prep phases: **D1** Playwright · **D2** Selenium · **D3** POM (pages + components) · part of **D4** (explicit waits in helpers).

## Why

Tests should not call raw browser APIs in every file: a client owns browser/driver lifecycle; page objects own locators and actions; components own reusable waits/flash. Base URL and UI timeout come from settings/env.

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
| `LAB_FW_UI_TIMEOUT_S` | UI timeout in **seconds** (default `120`); API timeout is separate (`LAB_FW_TIMEOUT_S`) |

Empty `LAB_FW_UI_BASE_URL` → `UiError` when creating a client.  
`ui_timeout_s <= 0` or non-float → `ConfigError`.

Helpers (single source for ms/s):

- `lab_fw.ui.timeouts.ui_timeout_s()` — seconds (Selenium / `WebDriverWait` / page load)
- `lab_fw.ui.timeouts.ui_timeout_ms()` — milliseconds (Playwright)

Clients, `BasePage.goto`, `PlaywrightWait` / `SeleniumWait`, and Flash read timeout via these helpers (env → `get_settings()`).

Demo: [the-internet.herokuapp.com](https://the-internet.herokuapp.com/) (login / secure). The external site **flakes** (blank page / Application error) — infra, not a POM defect. For a stable run: open login manually first; run UI and API separately.

---

## Structure (D3 POM)

```text
lab_fw/ui/
  client.py              # UIClient (Playwright)
  selenium_client.py     # SeleniumClient
  base_page.py           # BasePage / BasePageSelenium
  timeouts.py            # ui_timeout_s / ui_timeout_ms
  pages/                 # Playwright pages
  selenium_pages/        # Selenium pages
  components/
    playwright_wait.py   # PlaywrightWait
    selenium_wait.py     # SeleniumWait
    flash_message.py     # FlashMessage / FlashMessageSelenium
```

**Rule:** the same `page` / `driver` is passed into page, wait, and flash — one tab/session, not new browsers.

---

## Playwright (primary) — `UIClient`

```python
from lab_fw.ui.client import UIClient
from lab_fw.ui.pages.login_page import LoginPage
from lab_fw.core.config import get_settings

settings = get_settings()
with UIClient(settings) as ui:
    login = LoginPage(ui.page)
    login.open()
    secure = login.login("tomsmith", "SuperSecretPassword!")
```

- `start()` / CM: Playwright → Chromium → context(`base_url=...`) → page; default timeout = `ui_timeout_ms()`
- pages: `lab_fw.ui.pages` (`LoginPage`, `SecurePage`) on `BasePage`
- locators: prefer **ID** (`#username`, `#password`)
- `PlaywrightWait`: `is_visible` → `bool`; `wait_visible` / `wait_url` → on timeout **`UiError`**
- `FlashMessage`: `#flash` + text check; timeout from `ui_timeout_ms()`
- after login/logout click, wait for URL (`**/secure`, `**/login`); failure → `UiError`
- fixtures: `ui_client`, `ui_client_module`
- marker: `@pytest.mark.ui`
- no `time.sleep`

```bash
pytest -m ui -vv --tb=line
```

---

## Selenium (D2) — `SeleniumClient`

Separate lifecycle and pages: `lab_fw.ui.selenium_client`, `lab_fw.ui.selenium_pages`.

```python
from lab_fw.ui.selenium_client import SeleniumClient
from lab_fw.ui.selenium_pages.login_page import LoginPage
from lab_fw.core.config import get_settings

settings = get_settings()
with SeleniumClient(settings) as sc:
    page = LoginPage(sc.driver, settings.ui_base_url)
    page.open()
    secure = page.login("tomsmith", "SuperSecretPassword!")
```

- Chrome + **Selenium Manager**; `set_page_load_timeout(ui_timeout_s())`
- Chrome options disable Password Manager / leak detection (otherwise a second login with the demo password can show “Change password” and break typing)
- pages on `BasePageSelenium`; prefer **ID** locators where possible
- `SeleniumWait`: `visible` / `clickable` / `url_contains` → timeout → **`UiError`**; `is_visible` / `is_clickable` → `bool`
- `FlashMessageSelenium`: xpath + `ui_timeout_s()`
- fixtures: `selenium_client`, `selenium_client_module`
- marker: `@pytest.mark.selenium`
- no `time.sleep`

```bash
pytest -m selenium -vv --tb=line
```

| | Playwright | Selenium |
|--|------------|----------|
| Client | `UIClient` | `SeleniumClient` |
| Pages | `ui.pages` | `ui.selenium_pages` |
| Marker | `ui` | `selenium` |
| Wait helper | `PlaywrightWait` | `SeleniumWait` |
| Timeout unit | ms | seconds |
| Fail navigation / hard wait | `UiError` | `UiError` |

---

## Error policy

| Action | Behavior |
|--|--|
| `is_visible` / `is_clickable` | timeout → `False` |
| `wait_visible`, `wait_url`, `visible`, `clickable`, `url_contains` | timeout → `UiError` |
| Failed login/logout (wrong URL) | `UiError` (do not mask with `return self`) |

---

## Running tests

More stable when split (API mocks are fast; UI depends on the demo site):

```bash
pytest -m "not ui and not selenium" -q
pytest -m ui -vv --tb=line
pytest -m selenium -vv --tb=line
```

Full suite: `pytest -q` (long; external-site flake possible).

URL asserts use `settings.ui_base_url`, not a hardcoded host.

Some module-scoped tests **intentionally** share one session (documented in docstrings); running such a test alone may fail.

Helper tests: `tests/test_timeouts.py`, `tests/test_playwright_wait.py`, `tests/test_selenium_wait.py`, `tests/test_flash.py`, `tests/test_selenium_flash.py`.

## Why Playwright primary

Stable auto-waits and a convenient sync API. Selenium is the second stack for HP’s “Selenium / Playwright” expectation — know both, without cloning the entire suite one-to-one.
