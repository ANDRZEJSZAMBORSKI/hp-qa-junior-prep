# lab_fw reporting

[RU](README.md) · **EN** · [PL](README.pl.md)

Framework reporting layer. Tests and `ApiClient` call this API, not `allure` directly.

## Install

```bash
pip install -e ".[dev]"
```

`dev` includes `allure-pytest`. Without it, layer functions are no-ops (the suite still runs).

## API

| Function / decorator | Purpose |
|----------------------|---------|
| `step(title)` | report step (context manager) |
| `attach_text(name, body)` | text attachment |
| `attach_json(name, data)` | JSON attachment |
| `@epic(value)` | epic in Behaviors |
| `@feature(value)` | feature in Behaviors |
| `@title(value)` | test title in the report |
| `@description(value)` | description |
| `@severity(SeverityLevel.*)` | severity (`SeverityLevel` enum) |
| `@testcase(url, name=…)` | TMS link → TestRail case (N2) |
| `@issue(url, name=…)` | link → Jira issue (N2) |

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

`ApiClient` opens a `METHOD /path` step and, on success, attaches a truncated response.

## Allure metadata (N1)

With `--alluredir`, root `tests/conftest.py`:

- copies **`categories.json`** from the repo root into the results folder;
- writes **`environment.properties`** (pytest/allure versions, OS, Python, Local / Docker / GitHub Actions).

A static `environment.properties` in the repo is **not** used — see the commented example in `.github/workflows/ci.yml`.

## Run with Allure

```bash
pytest -q --alluredir=allure-results
allure serve allure-results
```

`allure-results/` and `allure-report/` are in `.gitignore`.

## TestRail and Jira (N2)

With `--alluredir`, `testcase` / `issue` show under **Links** in Allure. In TestRail, **References** on a case points to the pytest node id; run upload uses **trcli** (channel B). Details: [N2](../../../README.en.md#n2--jira--testrail) in the root README.

## Layer tests

```bash
pytest -m reporting -q
```
