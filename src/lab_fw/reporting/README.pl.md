# lab_fw reporting

[RU](README.md) · [EN](README.en.md) · **PL**

Warstwa raportowania frameworka. Testy i `ApiClient` wołają to API, a nie `allure` bezpośrednio.

## Instalacja

```bash
pip install -e ".[dev]"
```

W `dev` jest `allure-pytest`. Bez niego funkcje warstwy to no-op (suite działa dalej).

## API

| Funkcja | Cel |
|---------|-----|
| `step(title)` | krok raportu (context manager) |
| `attach_text(name, body)` | załącznik tekstowy |
| `attach_json(name, data)` | załącznik JSON |

```python
from lab_fw.reporting import step, attach_text, attach_json

with step("load users"):
    attach_json("payload", {"ok": True})
```

`ApiClient` sam otwiera krok `METHOD /path` i przy sukcesie dołącza obcięty response.

## Uruchomienie z Allure

```bash
pytest -q --alluredir=allure-results
```

Katalogi `allure-results/` i `allure-report/` są w `.gitignore`.

Opcjonalnie (jeśli jest Allure CLI):

```bash
allure serve allure-results
```

## Testy warstwy

```bash
pytest -q tests/test_reporting.py
```
