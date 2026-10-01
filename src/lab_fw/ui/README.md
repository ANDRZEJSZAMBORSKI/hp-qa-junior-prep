# lab_fw UI

**RU** · [EN](README.en.md) · [PL](README.pl.md)

UI-слой фреймворка: **Playwright = primary**, **Selenium = second stack** (D2). Стек не смешиваем в одном page-классе.

## Зачем

Тесты не дергают сырой браузерный API в каждом файле: клиент поднимает browser/driver, page objects инкапсулируют локаторы и действия. Base URL — из settings/env.

## Установка

```bash
pip install -e ".[dev]"
playwright install chromium
```

В `dev`: `playwright`, `selenium`. Для Playwright нужен бинарник Chromium (команда выше). Selenium 4 тянет драйвер через **Selenium Manager** (отдельный chromedriver вручную обычно не нужен).

## Settings

| Env | Назначение |
|-----|------------|
| `LAB_FW_UI_BASE_URL` | base URL UI (default `https://the-internet.herokuapp.com`) |

Пустой URL → `UiError` при создании клиента.

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
- фикстуры: `ui_client`, `ui_client_module`  
- маркер: `@pytest.mark.ui`  
- waits: auto-wait Playwright, без `time.sleep`

```bash
pytest -m ui -q
```

---

## Selenium (D2) — `SeleniumClient`

Отдельный lifecycle и отдельные pages: `lab_fw.ui.selenium_client`, `lab_fw.ui.selenium_pages`.

```python
from lab_fw.ui.selenium_client import SeleniumClient
from lab_fw.ui.selenium_pages.login_page import LoginPage
from lab_fw.core.config import get_settings

with SeleniumClient(get_settings()) as sc:
    page = LoginPage(sc.driver, settings.ui_base_url)
    page.open()
```

- Chrome + **Selenium Manager**  
- Chrome options глушат Password Manager / leak detection (иначе на втором login demo-пароля всплывает «Смените пароль» и ломает ввод)  
- pages на `BasePage`; локаторы с **ID** где можно (`#username`, `#password`)  
- waits: `WebDriverWait` + `expected_conditions` (explicit), без `time.sleep`  
- неуспешный переход login/logout → `UiError` (не маскируем `return self`)  
- фикстуры: `selenium_client`, `selenium_client_module`  
- маркер: `@pytest.mark.selenium`

```bash
pytest -m selenium -q
```

| | Playwright | Selenium |
|--|------------|----------|
| Клиент | `UIClient` | `SeleniumClient` |
| Pages | `ui.pages` | `ui.selenium_pages` |
| Marker | `ui` | `selenium` |
| Wait | auto-wait | explicit `WebDriverWait` |

---

## Общий прогон

```bash
pytest -m ui -q
pytest -m selenium -q
pytest -q
```

Ассерты URL — через `settings.ui_base_url`, без хардкода хоста.

Часть module-scope тестов **намеренно** делит одну сессию (shared state) — в docstring; один такой тест отдельно может упасть.

## Почему Playwright primary

Стабильные auto-waits и удобный sync API. Selenium нужен как второй стек под требования HP («Selenium / Playwright») — уметь читать/писать оба, не дублировать весь suite один-в-один.
