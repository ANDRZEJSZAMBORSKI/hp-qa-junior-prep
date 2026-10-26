# lab_fw reporting

[RU](README.md) · [EN](README.en.md) · **PL**

Warstwa raportowania frameworka. Testy i `ApiClient` wołają to API, a nie `allure` bezpośrednio.

## Instalacja

```bash
pip install -e ".[dev]"
```

W `dev` jest `allure-pytest`. Bez niego funkcje warstwy to no-op (suite działa dalej).

## API

| Funkcja / dekorator | Przeznaczenie |
|---------------------|---------------|
| `step(title)` | krok raportu (context manager) |
| `attach_text(name, body)` | załącznik tekstowy |
| `attach_json(name, data)` | załącznik JSON |
| `@epic(value)` | epic w Behaviors |
| `@feature(value)` | feature w Behaviors |
| `@title(value)` | tytuł testu w raporcie |
| `@description(value)` | opis |
| `@severity(SeverityLevel.*)` | severity (enum `SeverityLevel`) |
| `@testcase(url, name=…)` | link TMS → case TestRail (Lab N2) |
| `@issue(url, name=…)` | link → issue Jira (Lab N2) |

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

`ApiClient` otwiera krok `METHOD /path` i przy sukcesie dołącza obcięty response.

## Metadane Allure (Lab N1)

Przy `--alluredir` rootowy `tests/conftest.py`:

- kopiuje **`categories.json`** z katalogu głównego repo do folderu wyników;
- zapisuje **`environment.properties`** (wersje pytest/allure, OS, Python, Local / Docker / GitHub Actions).

Statyczny `environment.properties` w repo **nie jest używany** — patrz zakomentowany przykład w `.github/workflows/ci.yml`.

## Uruchomienie z Allure

```bash
pytest -q --alluredir=allure-results
allure serve allure-results
```

Katalogi `allure-results/` i `allure-report/` są w `.gitignore`.

## Test management (Lab N2)

Przy `--alluredir` dekoratory `testcase` / `issue` trafiają do **Links** w Allure. Powiązanie w TestRail — pole **References** na case (node id pytest). Upload runu przez **trcli** — [Lab N2](../../../README.pl.md#lab-n2--jira--testrail-trial) w README głównym.

## Testy warstwy

```bash
pytest -m reporting -q
```
