# lab_fw reporting

**RU** · [EN](README.en.md) · [PL](README.pl.md)

Слой отчёта фреймворка. Тесты и `ApiClient` вызывают этот API, а не `allure` напрямую.

## Установка

```bash
pip install -e ".[dev]"
```

В `dev` есть `allure-pytest`. Без него функции слоя — no-op (прогон не падает).

## API

| Функция | Назначение |
|---------|------------|
| `step(title)` | шаг отчёта (context manager) |
| `attach_text(name, body)` | текстовый attachment |
| `attach_json(name, data)` | JSON attachment |

```python
from lab_fw.reporting import step, attach_text, attach_json

with step("load users"):
    attach_json("payload", {"ok": True})
```

`ApiClient` сам открывает шаг `METHOD /path` и при успехе аттачит обрезанный response.

## Прогон с Allure

```bash
pytest -q --alluredir=allure-results
```

Папки `allure-results/` и `allure-report/` в `.gitignore`.

Опционально (если установлен Allure CLI):

```bash
allure serve allure-results
```

## Тесты слоя

```bash
pytest -q tests/test_reporting.py
```
