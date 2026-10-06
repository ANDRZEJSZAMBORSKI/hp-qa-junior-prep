# hp-qa-junior-prep

[RU](README.md) · [EN](README.en.md) · **PL**

Repo szkoleniowe Junior QA Automation (Python): framework pytest `lab_fw`, API (httpx), UI (Playwright / Selenium), mocki, Allure, Docker, Docker Compose, GitHub Actions.

## Szybki start (lokalnie)

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
# .venv\Scripts\activate       # Windows cmd/PowerShell

pip install -e ".[dev]"
pytest -m "not ui and not selenium and not compose" -q -n auto
```

Testy UI (wymagana przeglądarka):

```bash
playwright install chromium
pytest -m ui -q
pytest -m selenium -q
```

## Struktura

| Ścieżka | Przeznaczenie |
|---------|---------------|
| `src/lab_fw/` | framework (api, ui, config, reporting, plugin pytest) |
| `tests/` | suite pytest |
| `Dockerfile` | multi-stage: `local` (CA Avast) / `ci` |
| `docker-compose.yml` | `mock-api` + `tests` |
| `.github/workflows/tests.yml` | unit/API na runnerze (bez UI/compose) |
| `.github/workflows/ci.yml` | Docker Compose na GitHub Actions |

## Zmienne środowiskowe

| Env | Przeznaczenie |
|-----|---------------|
| `LAB_FW_BASE_URL` | API base URL (domyślnie `https://example.com`) |
| `LAB_FW_UI_BASE_URL` | UI base URL (domyślnie the-internet.herokuapp.com) |
| `LAB_FW_API_TOKEN` | opcjonalny Bearer token |
| `LAB_FW_TIMEOUT_S` / `LAB_FW_UI_TIMEOUT_S` | timeouty |
| `LAB_FW_LOG_LEVEL` | poziom logów |

Sekret CI: GitHub → Settings → Secrets → `LAB_FW_API_TOKEN`.

## Markery pytest

| Marker | Znaczenie |
|--------|-----------|
| `smoke` / `api` / … | zwykłe szybkie testy |
| `ui` | prawdziwy Playwright |
| `selenium` | prawdziwy Selenium |
| `compose` | wymaga usługi `mock-api` z Compose |

## Docker

### Obrazy (`Dockerfile`)

- **`ci`** — na GitHub / Linux bez firmowego MITM
- **`local`** — kopiuje `avast-root.crt` (plik lokalny, nie w git)

`Dockerfile.local` i `avast-root.crt` są w `.gitignore`.

```bash
docker build --target ci -t hp-qa-junior-prep:ci .
docker run --rm -e LAB_FW_API_TOKEN=ci-demo-token hp-qa-junior-prep:ci

docker build --target local -t hp-qa-junior-prep:local .
docker run --rm -e LAB_FW_API_TOKEN=ci-demo-token hp-qa-junior-prep:local
```

CMD obrazu: `pytest -m "not ui and not selenium"` — **obejmuje** testy `compose`, gdy dostępny jest `mock-api`.

### Docker Compose

```bash
docker compose up --build --abort-on-container-exit

DOCKER_TARGET=local docker compose up --build --abort-on-container-exit
```

Usługi: `mock-api` (MockServer `:1080`) + `tests` (build + pytest).

`LAB_FW_BASE_URL` **nie** jest ustawiane globalnie w compose (starsze testy oczekują `example.com` / MockTransport). Testy compose wołają `http://mock-api:1080` wprost.

## GitHub Actions

| Workflow | Co robi |
|----------|---------|
| **tests** | `pip install` + `pytest -m "not ui and not selenium and not compose"` + artefakt Allure |
| **CI** | `docker compose` z `DOCKER_TARGET=ci` — także `@pytest.mark.compose` |

| Gdzie | mock-api? | Testy compose |
|-------|-----------|---------------|
| **CI** / lokalny compose | tak | uruchamiane |
| workflow **tests** | nie | wykluczone (`not compose`) |

## Allure

```bash
pytest -q --alluredir=allure-results
allure serve allure-results
```

Upload artefaktu używa `if: always()`.

## Dokumentacja modułów

- [API](src/lab_fw/api/README.pl.md)
- [UI](src/lab_fw/ui/README.pl.md)
- [Reporting / Allure](src/lab_fw/reporting/README.pl.md)
- [Pytest plugin](src/lab_fw/pytest_plugin/README.pl.md)
- [Pytest notes](tests/README_PYTEST.pl.md)
- [Mocks lab](tests/mocks_lab/README.pl.md)

## Plan nauki

Zob. [PLAN_MID_HP.md](PLAN_MID_HP.md).
