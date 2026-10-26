### О разделе

Минимальный путь от пустой машины до «зелёного» прогона unit/API без браузера и без MockServer. Это тот же набор, что workflow **tests** на GitHub (без маркера `compose`).

### Пошагово

1. Клонируй репозиторий, перейди в корень.
2. Создай venv на **Python 3.11+** и активируй его.
3. `pip install -e ".[dev]"` — editable install пакета `lab-fw` и dev-зависимостей (pytest, xdist, allure, playwright, selenium, filelock).
4. Запусти быстрый suite (см. команду ниже). Ожидание: сотни passed, 0 failed; время — минуты на ноутбуке.

### Что означает фильтр маркеров

`-m "not ui and not selenium and not compose"` исключает тесты, которым нужен реальный браузер или контейнер `mock-api`. Так локально не нужны Docker и `playwright install` для первого успеха.

### UI (отдельный шаг)

Playwright и Selenium требуют браузер. Playwright: `playwright install chromium`. Selenium 4 на Windows часто тянет Chrome через Selenium Manager автоматически.

### Самопроверка

| Вопрос | Где ответ |
|--------|-----------|
| Пакет установлен editable? | `python -m pip show lab-fw` → Location внутри твоего `.venv` |
| xdist работает? | В выводе pytest есть `[gw0]` при `-n auto` |
| Почему не бегут compose-тесты? | Нет MockServer — см. раздел Docker |

### Типичные проблемы

- **`python` не 3.11** — переустанови venv с нужной версией.
- **Import errors** — активирован ли venv; выполнен ли `pip install -e ".[dev]"`.
- **Playwright без браузера** — не запускай `-m ui` до `playwright install`.
