# lab_fw UI

**RU** · [EN](README.en.md) · [PL](README.pl.md)

UI-слой фреймворка: **Playwright = primary**, **Selenium = second stack** (D2). Стек не смешиваем в одном page-классе.

Фазы prep: **D1** Playwright · **D2** Selenium · **D3** POM (pages + components) · часть **D4** (explicit waits в helpers).

## Зачем

Тесты не дергают сырой браузерный API в каждом файле: клиент поднимает browser/driver, page objects инкапсулируют локаторы и действия, components — переиспользуемые waits/flash. Base URL и UI timeout — из settings/env.

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
| `LAB_FW_UI_TIMEOUT_S` | UI timeout в **секундах** (default `120`); API timeout — отдельно `LAB_FW_TIMEOUT_S` |

Пустой `LAB_FW_UI_BASE_URL` → `UiError` при создании клиента.  
`ui_timeout_s <= 0` или не-float → `ConfigError`.

Хелперы (один источник для ms/s):

- `lab_fw.ui.timeouts.ui_timeout_s()` — секунды (Selenium / `WebDriverWait` / page load)
- `lab_fw.ui.timeouts.ui_timeout_ms()` — миллисекунды (Playwright)

Клиенты, `BasePage.goto`, `PlaywrightWait` / `SeleniumWait`, Flash читают timeout через эти хелперы (env → `get_settings()`).

Demo: [the-internet.herokuapp.com](https://the-internet.herokuapp.com/) (login / secure). Внешний стенд **флакует** (пустая страница / Application error) — это infra, не дефект POM. Для стабильного прогона: сначала проверить login вручную; UI и API гонять раздельно.

---

## Структура (D3 POM)

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

**Правило:** один и тот же `page` / `driver` передаётся в page, wait и flash — это одна вкладка/сессия, не новые браузеры.

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
- pages: `lab_fw.ui.pages` (`LoginPage`, `SecurePage`) на `BasePage`
- локаторы: предпочтительно **ID** (`#username`, `#password`)
- `PlaywrightWait`: `is_visible` → `bool`; `wait_visible` / `wait_url` → при timeout **`UiError`**
- `FlashMessage`: `#flash` + проверка текста; timeout из `ui_timeout_ms()`
- login/logout после click ждут URL (`**/secure`, `**/login`); неуспех → `UiError`
- фикстуры: `ui_client`, `ui_client_module`
- маркер: `@pytest.mark.ui`
- без `time.sleep`

```bash
pytest -m ui -vv --tb=line
```

---

## Selenium (D2) — `SeleniumClient`

Отдельный lifecycle и pages: `lab_fw.ui.selenium_client`, `lab_fw.ui.selenium_pages`.

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
- Chrome options глушат Password Manager / leak detection (иначе на втором login demo-пароля всплывает «Смените пароль» и ломает ввод)
- pages на `BasePageSelenium`; локаторы с **ID** где можно
- `SeleniumWait`: `visible` / `clickable` / `url_contains` → timeout → **`UiError`**; `is_visible` / `is_clickable` → `bool`
- `FlashMessageSelenium`: xpath + `ui_timeout_s()`
- фикстуры: `selenium_client`, `selenium_client_module`
- маркер: `@pytest.mark.selenium`
- без `time.sleep`

```bash
pytest -m selenium -vv --tb=line
```

| | Playwright | Selenium |
|--|------------|----------|
| Клиент | `UIClient` | `SeleniumClient` |
| Pages | `ui.pages` | `ui.selenium_pages` |
| Marker | `ui` | `selenium` |
| Wait helper | `PlaywrightWait` | `SeleniumWait` |
| Timeout unit | ms | seconds |
| Fail navigation / hard wait | `UiError` | `UiError` |

---

## Политика ошибок

| Действие | Поведение |
|--|--|
| `is_visible` / `is_clickable` | timeout → `False` |
| `wait_visible`, `wait_url`, `visible`, `clickable`, `url_contains` | timeout → `UiError` |
| Неуспешный login/logout (нет нужного URL) | `UiError` (не маскировать `return self`) |

---

## Прогон

Стабильнее раздельно (API mock-ы быстрые; UI зависит от demo-сайта):

```bash
pytest -m "not ui and not selenium" -q
pytest -m ui -vv --tb=line
pytest -m selenium -vv --tb=line
```

Полный suite: `pytest -q` (долго; flake внешнего сайта возможен).

Ассерты URL — через `settings.ui_base_url`, без хардкода хоста.

Часть module-scope тестов **намеренно** делит одну сессию (shared state) — в docstring; один такой тест отдельно может упасть.

Тесты helpers: `tests/test_timeouts.py`, `tests/test_playwright_wait.py`, `tests/test_selenium_wait.py`, `tests/test_flash.py`, `tests/test_selenium_flash.py`.

## Почему Playwright primary

Стабильные auto-waits и удобный sync API. Selenium нужен как второй стек под требования HP («Selenium / Playwright») — уметь читать/писать оба, не дублировать весь suite один-в-один.
