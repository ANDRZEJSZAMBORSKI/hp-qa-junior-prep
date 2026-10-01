# lab_fw UI

[RU](README.md) · [EN](README.en.md) · **PL**

Warstwa UI frameworka na **Playwright** (primary). Selenium — później w fazie D.

## Po co

Testy nie wołają surowego Playwright w każdym pliku: `UIClient` uruchamia Chromium + context/page; page objects (`LoginPage`, `SecurePage`) trzymają lokatory i akcje. Base URL pochodzi z settings/env.

## Instalacja

```bash
pip install -e ".[dev]"
playwright install chromium
```

`playwright` jest w optional `dev`. Potrzebny jest **binarny Chromium** (komenda powyżej), inaczej `BrowserType.launch` się wywali.

## Settings

| Env | Cel |
|-----|-----|
| `LAB_FW_UI_BASE_URL` | base URL UI (domyślnie `https://the-internet.herokuapp.com`) |

Pusty URL → `UiError` przy tworzeniu `UIClient`.

## UIClient

```python
from lab_fw.ui.client import UIClient
from lab_fw.core.config import get_settings

with UIClient(get_settings()) as ui:
    ui.page.goto("/login")
```

- `start()` / context manager: Playwright → Chromium → context(`base_url=...`) → page  
- `close()` / `__exit__`: zamyka page/context/browser/playwright  
- dostęp: `ui.page`, `ui.settings`

Fixtury w `tests/conftest.py`: `ui_client` (function) oraz `ui_client_module` (module, wspólna sesja).

## Page objects

| Klasa | path | Idea |
|-------|------|------|
| `LoginPage` | `/login` | pola, login → zwraca `SecurePage` |
| `SecurePage` | `/secure` | logout → zwraca `LoginPage` |

Obie dziedziczą `lab_fw.abstractions.BasePage` (`open`, `path`). Waity — auto-wait Playwright / lokatory, bez `time.sleep`.

Demo: [the-internet.herokuapp.com](https://the-internet.herokuapp.com/) (login / secure).

## Uruchomienie

```bash
pytest -m ui -q
pytest -q
```

Marker `ui` jest w `pyproject.toml`.

Assercje URL budują się z `settings.ui_base_url`, bez hardcodu hosta.

Część testów module-scope **celowo** dzieli jedną `page` (opis w docstringu); sam taki test może paść.

## Dlaczego Playwright primary

Stabilne auto-waity, jedno API Chromium, wygodne sync API w Pythonie. Selenium pojawi się jako D2 (drugi stack), nie jako zamiennik.
