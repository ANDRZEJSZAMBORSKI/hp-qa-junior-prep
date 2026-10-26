# lab_fw reporting

**RU** · [EN](README.en.md) · [PL](README.pl.md)

Слой отчёта фреймворка. Тесты и `ApiClient` вызывают этот API, а не `allure` напрямую.

## Установка

```bash
pip install -e ".[dev]"
```

В `dev` есть `allure-pytest`. Без него функции слоя — no-op (прогон не падает).

## API

| Функция / декоратор | Назначение |
|---------------------|------------|
| `step(title)` | шаг отчёта (context manager) |
| `attach_text(name, body)` | текстовый attachment |
| `attach_json(name, data)` | JSON attachment |
| `@epic(value)` | epic в Behaviors |
| `@feature(value)` | feature в Behaviors |
| `@title(value)` | заголовок теста в отчёте |
| `@description(value)` | описание |
| `@severity(SeverityLevel.*)` | severity (enum `SeverityLevel`) |
| `@testcase(url, name=…)` | ссылка TMS → TestRail case (Lab N2) |
| `@issue(url, name=…)` | ссылка → Jira issue (Lab N2) |

```python
from lab_fw.reporting import step, attach_json, feature, severity, SeverityLevel
from lab_fw.reporting import testcase, issue

@issue("https://example.atlassian.net/browse/QA-1")
@testcase("https://example.testrail.io/index.php?/cases/view/1", name="C1")
@feature("API Client")
@severity(SeverityLevel.CRITICAL)
def test_example():
    with step("call API"):
        attach_json("payload", {"ok": True})
```

`ApiClient` сам открывает шаг `METHOD /path` и при успехе аттачит обрезанный response.

## Метаданные Allure (Lab N1)

При `--alluredir` корневой `tests/conftest.py`:

- копирует **`categories.json`** из корня репо в папку результатов;
- пишет **`environment.properties`** (версии pytest/allure, OS, Python, Local / Docker / GitHub Actions).

Статический `environment.properties` в репо **не используется** — см. закомментированный пример в `.github/workflows/ci.yml`.

## Прогон с Allure

```bash
pytest -q --alluredir=allure-results
allure serve allure-results
```

Папки `allure-results/` и `allure-report/` в `.gitignore`.

## TestRail и Jira (Lab N2)

При `--alluredir` декораторы `testcase` / `issue` попадают в **Links** отчёта Allure. В TestRail на кейсе поле **References** связывает case с pytest node id; загрузка run — через **trcli** (канал B). Подробно: [Lab N2](../../../README.md#lab-n2--jira--testrail-trial) в корневом README.

## Тесты слоя

```bash
pytest -m reporting -q
```
