# lab_fw UI

**RU** · [EN](README.en.md) · [PL](README.pl.md)

UI-слой фреймворка на **Playwright** (primary). Selenium — отдельный шаг фазы D позже.

## Зачем

Тесты не дергают сырой Playwright в каждом файле: `UIClient` поднимает Chromium + context/page, page objects (`LoginPage`, `SecurePage`) инкапсулируют локаторы и действия. Base URL — из settings/env.

## Установка

```bash
pip install -e ".[dev]"
playwright install chromium
```

`playwright` — в optional `dev`. Нужен **бинарник Chromium** (команда выше), иначе `BrowserType.launch` упадёт.

## Settings

| Env | Назначение |
|-----|------------|
| `LAB_FW_UI_BASE_URL` | base URL UI (default `https://the-internet.herokuapp.com`) |

Пустой URL → `UiError` при создании `UIClient`.

## UIClient

```python
from lab_fw.ui.client import UIClient
from lab_fw.core.config import get_settings

with UIClient(get_settings()) as ui:
    ui.page.goto("/login")
```

- `start()` / context manager: Playwright → Chromium → context(`base_url=...`) → page  
- `close()` / `__exit__`: page/context/browser/playwright  
- доступ: `ui.page`, `ui.settings`

Фикстуры в `tests/conftest.py`: `ui_client` (function) и `ui_client_module` (module, shared session).

## Page objects

| Класс | path | Идея |
|-------|------|------|
| `LoginPage` | `/login` | поля, login → возвращает `SecurePage` |
| `SecurePage` | `/secure` | logout → возвращает `LoginPage` |

Оба наследуют `lab_fw.abstractions.BasePage` (`open`, `path`). Waits — auto-wait Playwright / locators, без `time.sleep`.

Demo-сайт: [the-internet.herokuapp.com](https://the-internet.herokuapp.com/) (login / secure).

## Прогон

```bash
pytest -m ui -q
pytest -q
```

Маркер `ui` зарегистрирован в `pyproject.toml`.

Ассерты URL строят от `settings.ui_base_url`, не хардкодят хост.

Часть module-scope тестов **намеренно** делит одну `page` (shared state) — в docstring теста указано; один такой тест отдельно может упасть.

## Почему Playwright primary

Стабильные auto-waits, один API для Chromium, удобный sync Python API. Selenium в репо появится как D2 (второй стек), не как замена.
