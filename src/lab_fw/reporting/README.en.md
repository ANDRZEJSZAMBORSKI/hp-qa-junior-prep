# lab_fw reporting

[RU](README.md) · **EN** · [PL](README.pl.md)

Framework reporting layer. Tests and `ApiClient` call this API, not `allure` directly.

## Install

```bash
pip install -e ".[dev]"
```

`dev` includes `allure-pytest`. Without it, layer functions are no-ops (the suite still runs).

## API

| Function | Purpose |
|----------|---------|
| `step(title)` | report step (context manager) |
| `attach_text(name, body)` | text attachment |
| `attach_json(name, data)` | JSON attachment |

```python
from lab_fw.reporting import step, attach_text, attach_json

with step("load users"):
    attach_json("payload", {"ok": True})
```

`ApiClient` opens a `METHOD /path` step and, on success, attaches a truncated response.

## Run with Allure

```bash
pytest -q --alluredir=allure-results
```

`allure-results/` and `allure-report/` are in `.gitignore`.

Optional (if Allure CLI is installed):

```bash
allure serve allure-results
```

## Layer tests

```bash
pytest -q tests/test_reporting.py
```
