# lab_fw UI

[RU](README.md) · [EN](README.en.md) · **PL**

Warstwa UI: **Playwright = primary**, **Selenium = drugi stack** (D2). Nie mieszamy stacków w jednej klasie page.

Fazy prep: **D1** Playwright · **D2** Selenium · **D3** POM (pages + components) · część **D4** (explicit waits w helperach).

## Po co

Testy nie wołają surowego API przeglądarki w każdym pliku: klient trzyma lifecycle browser/driver, page objects — lokatory i akcje, components — waity/flash. Base URL i UI timeout z settings/env.

## Instalacja

```bash
pip install -e ".[dev]"
playwright install chromium
```

W `dev`: `playwright`, `selenium`. Playwright wymaga binariów Chromium (komenda powyżej). Selenium 4 używa **Selenium Manager** (ręczny chromedriver zwykle zbędny).

## Settings

| Env | Cel |
|-----|-----|
| `LAB_FW_UI_BASE_URL` | base URL UI (domyślnie `https://the-internet.herokuapp.com`) |
| `LAB_FW_UI_TIMEOUT_S` | timeout UI w **sekundach** (domyślnie `120`); timeout API osobno (`LAB_FW_TIMEOUT_S`) |

Pusty `LAB_FW_UI_BASE_URL` → `UiError` przy tworzeniu klienta.  
`ui_timeout_s <= 0` lub nie-float → `ConfigError`.

Helpery (jedno źródło ms/s):

- `lab_fw.ui.timeouts.ui_timeout_s()` — sekundy (Selenium / `WebDriverWait` / page load)
- `lab_fw.ui.timeouts.ui_timeout_ms()` — milisekundy (Playwright)

Klienci, `BasePage.goto`, `PlaywrightWait` / `SeleniumWait`, Flash czytają timeout przez te helpery (env → `get_settings()`).

Demo: [the-internet.herokuapp.com](https://the-internet.herokuapp.com/) (login / secure). Zewnętrzny site **flakuje** (pusta strona / Application error) — infra, nie defekt POM. Na stabilny przebieg: najpierw login ręcznie; UI i API osobno.

---

## Struktura (D3 POM)

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

**Zasada:** ten sam `page` / `driver` trafia do page, wait i flash — jedna karta/sesja, nie nowe przeglądarki.

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
- pages: `lab_fw.ui.pages` (`LoginPage`, `SecurePage`) na `BasePage`
- lokatory: preferuj **ID** (`#username`, `#password`)
- `PlaywrightWait`: `is_visible` → `bool`; `wait_visible` / `wait_url` → przy timeout **`UiError`**
- `FlashMessage`: `#flash` + sprawdzenie tekstu; timeout z `ui_timeout_ms()`
- po login/logout click czekamy na URL (`**/secure`, `**/login`); porażka → `UiError`
- fixtury: `ui_client`, `ui_client_module`
- marker: `@pytest.mark.ui`
- bez `time.sleep`

```bash
pytest -m ui -vv --tb=line
```

---

## Selenium (D2) — `SeleniumClient`

Osobny lifecycle i pages: `lab_fw.ui.selenium_client`, `lab_fw.ui.selenium_pages`.

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
- Opcje Chrome wyłączają Password Manager / leak detection (inaczej drugie logowanie demo-hasłem może pokazać „Zmień hasło” i zepsuć wpisywanie)
- pages na `BasePageSelenium`; lokatory **ID** gdzie się da
- `SeleniumWait`: `visible` / `clickable` / `url_contains` → timeout → **`UiError`**; `is_visible` / `is_clickable` → `bool`
- `FlashMessageSelenium`: xpath + `ui_timeout_s()`
- fixtury: `selenium_client`, `selenium_client_module`
- marker: `@pytest.mark.selenium`
- bez `time.sleep`

```bash
pytest -m selenium -vv --tb=line
```

| | Playwright | Selenium |
|--|------------|----------|
| Klient | `UIClient` | `SeleniumClient` |
| Pages | `ui.pages` | `ui.selenium_pages` |
| Marker | `ui` | `selenium` |
| Wait helper | `PlaywrightWait` | `SeleniumWait` |
| Jednostka timeout | ms | sekundy |
| Fail nawigacji / hard wait | `UiError` | `UiError` |

---

## Polityka błędów

| Akcja | Zachowanie |
|--|--|
| `is_visible` / `is_clickable` | timeout → `False` |
| `wait_visible`, `wait_url`, `visible`, `clickable`, `url_contains` | timeout → `UiError` |
| Nieudany login/logout (zły URL) | `UiError` (bez maskowania `return self`) |

---

## Uruchamianie

Stabilniej osobno (API mocki szybkie; UI zależy od demo-site):

```bash
pytest -m "not ui and not selenium" -q
pytest -m ui -vv --tb=line
pytest -m selenium -vv --tb=line
```

Pełny suite: `pytest -q` (długo; możliwy flake zewnętrznego site).

Assercje URL przez `settings.ui_base_url`, bez hardcodu hosta.

Część testów module-scope **celowo** dzieli sesję (opis w docstringu); sam taki test może paść.

Testy helperów: `tests/test_timeouts.py`, `tests/test_playwright_wait.py`, `tests/test_selenium_wait.py`, `tests/test_flash.py`, `tests/test_selenium_flash.py`.

## Dlaczego Playwright primary

Stabilne auto-waity i wygodne sync API. Selenium to drugi stack pod wymaganie HP („Selenium / Playwright”) — znać oba, bez klonowania całego suite 1:1.
