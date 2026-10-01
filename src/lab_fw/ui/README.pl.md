# lab_fw UI

[RU](README.md) · [EN](README.en.md) · **PL**

Warstwa UI: **Playwright = primary**, **Selenium = drugi stack** (D2). Nie mieszamy stacków w jednej klasie page.

## Po co

Testy nie wołają surowego API przeglądarki w każdym pliku: klient trzyma lifecycle browser/driver, page objects — lokatory i akcje. Base URL z settings/env.

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

Pusty URL → `UiError` przy tworzeniu klienta.

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
- fixtury: `ui_client`, `ui_client_module`  
- marker: `@pytest.mark.ui`  
- waity: auto-wait Playwright, bez `time.sleep`

```bash
pytest -m ui -q
```

---

## Selenium (D2) — `SeleniumClient`

Osobny lifecycle i pages: `lab_fw.ui.selenium_client`, `lab_fw.ui.selenium_pages`.

```python
from lab_fw.ui.selenium_client import SeleniumClient
from lab_fw.ui.selenium_pages.login_page import LoginPage
from lab_fw.core.config import get_settings

with SeleniumClient(get_settings()) as sc:
    page = LoginPage(sc.driver, settings.ui_base_url)
    page.open()
```

- Chrome + **Selenium Manager**  
- Opcje Chrome wyłączają Password Manager / leak detection (inaczej drugie logowanie demo-hasłem może pokazać „Zmień hasło” i zepsuć wpisywanie)  
- pages na `BasePage`; preferuj lokatory **ID** (`#username`, `#password`)  
- waity: `WebDriverWait` + `expected_conditions` (explicit), bez `time.sleep`  
- nieudana nawigacja login/logout → `UiError` (bez maskowania `return self`)  
- fixtury: `selenium_client`, `selenium_client_module`  
- marker: `@pytest.mark.selenium`

```bash
pytest -m selenium -q
```

| | Playwright | Selenium |
|--|------------|----------|
| Klient | `UIClient` | `SeleniumClient` |
| Pages | `ui.pages` | `ui.selenium_pages` |
| Marker | `ui` | `selenium` |
| Wait | auto-wait | explicit `WebDriverWait` |

---

## Pełny przebieg

```bash
pytest -m ui -q
pytest -m selenium -q
pytest -q
```

Assercje URL przez `settings.ui_base_url`, bez hardcodu hosta.

Część testów module-scope **celowo** dzieli sesję (opis w docstringu); sam taki test może paść.

## Dlaczego Playwright primary

Stabilne auto-waity i wygodne sync API. Selenium to drugi stack pod wymaganie HP („Selenium / Playwright”) — znać oba, bez klonowania całego suite 1:1.
