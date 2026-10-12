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

## Schemat interakcji API (lab I1)

Projekt ma dwa tryby testów API: izolowany `httpx.MockTransport` oraz integracyjny z osobnym MockServer przez Docker Compose. Prawdziwe cloud/API w tych przebiegach **nie** jest wołane — mock imituje kontrakt HTTP (status, JSON, nagłówki).

### Tryb 1. Zwykłe testy

```mermaid
flowchart TD
    A[pytest] --> B[API test]
    B --> C[ApiClient]
    C --> D[httpx.MockTransport]
    D --> E[Mock HTTP response]
```

`httpx.MockTransport` działa w procesie Pythona: sprawdzamy klienta HTTP bez osobnego serwera i bez realnego wywołania sieciowego API.

Workflow **tests** wyklucza marker `compose` — wymagane serwisy nie są tam uruchamiane.

### Tryb 2. Docker Compose / CI

```mermaid
flowchart TD
    A[Docker Compose] --> B[tests container]
    A --> C[mock-api container]
    B --> D[pytest]
    D --> E[ApiClient]
    E -->|HTTP GET /users/1| F[mock-api:1080]
    F -->|HTTP 200 + JSON + Content-Type| E
```

Testy działają w kontenerze `tests`, MockServer w `mock-api`. Komunikacja w sieci Compose: `http://mock-api:1080`.

Workflow **CI** uruchamia Compose z `DOCKER_TARGET=ci`, żeby testy integracyjne mogły trafić do MockServer.

### Po co oba poziomy

- **MockTransport** — szybko i izolowanie: odpowiedzi, błędy, kontrakt kodu klienta; łatwiej złapać błąd w logice `ApiClient`.
- **MockServer** — ruch HTTP między kontenerami i konfiguracja środowiska integracyjnego.

Oba podejścia ograniczają zależność od dostępności prawdziwego zewnętrznego API.

### Strategia mocków (lab I2)

| | `httpx.MockTransport` | MockServer |
|--|------------------------|------------|
| Gdzie działa | w procesie Pythona | osobna usługa (`mock-api`) |
| Sieć | niepotrzebna | prawdziwy HTTP w sieci Dockera |
| Cel | testy unit/API klienta | integracja kontenerów |
| Przykłady | `tests/mocks_lab/` | `tests/test_compose_api.py` |

Kontrakt Compose w `test_mock_api_users`:

1. fixture `reset_mockserver` — `PUT /mockserver/reset` przed i po teście (izolacja stanu);
2. `PUT /mockserver/expectation` → **201** (reguła przyjęta);
3. `ApiClient.get` → **200**, ciało JSON, `Content-Type` zawiera `application/json`;
4. `PUT /mockserver/verify` → **202** (żądanie faktycznie trafiło w expectation).

Marker `compose` sam nie uruchamia infrastruktury — patrz komenda:

- workflow **tests**: `pytest -m "not ui and not selenium and not compose"` (bez MockServer);
- **Dockerfile CMD**: `not ui and not selenium` (bez `not compose`) — w Compose jest `mock-api`, więc testy integracyjne lecą;
- celowane: `pytest -m compose` w serwisie `tests`.

`LAB_FW_BASE_URL` nie ustawiamy globalnie w Compose: testy compose podają `base_url="http://mock-api:1080"` wprost w `Settings`.

### Negatywne scenariusze integracyjne (lab I3)

W `tests/test_compose_api.py` (marker `compose`, ten sam `reset_mockserver`):

| Test | MockServer | Co sprawdzamy |
|------|------------|---------------|
| `test_mock_api_auth_fail` | `GET /protected` → **401** + JSON `error` | klient dostaje status/ciało/Content-Type bez prawdziwego IdP |
| `test_mock_api_timeout` | `GET /slow` z `delay` 1000 ms, `timeout_s=0.2` | `ApiError`; `__cause__` to `ReadTimeout` ⊂ `TimeoutException` ⊂ `HTTPError`; potem `/mockserver/verify` → **202** |

Polityka klienta: przy 4xx/5xx `get`/`post` **zwracają** `Response` (opcjonalnie `ensure_success` → `HttpStatusError`). Błędy transportu (timeout itd.) zawsze jako `ApiError`.

### Diagnostyka padających testów (lab I4)

| Objaw | Gdzie szukać | Co sprawdzić |
|---|---|---|
| Lokalny test nie przeszedł | Wynik `pytest` w terminalu | Nazwę testu, traceback, assertion i rzeczywisty wynik |
| Potrzebne są logi frameworka | Logi `lab_fw`; ustawienie `LAB_FW_LOG_LEVEL` | Poziom logowania i komunikaty klienta API |
| Potrzebne są szczegóły żądania i odpowiedzi HTTP | Raport Allure / załączniki | Załączniki `response` i `status_error`, jeśli zostały utworzone |
| Test Compose nie przeszedł | `docker compose logs tests` | Wynik pytest, traceback, konfigurację i zmienne środowiskowe kontenera |
| Wystąpił problem z MockServer | `docker compose logs mock-api` | Czy żądanie dotarło, czy zarejestrowano oczekiwanie i jaką odpowiedź zwrócono |
| Błąd w GitHub Actions | Actions → workflow → job → nieudany krok | Dla `tests` — krok pytest i artefakt `allure-results`; dla `CI` — krok `Run Docker Compose` |
| Nie zarejestrowano oczekiwania MockServer | Wynik rejestracji i logi `mock-api` | Status HTTP rejestracji (zwykle `201`) oraz treść odpowiedzi |
| Weryfikacja MockServer nie powiodła się | Wynik `/mockserver/verify` i logi `mock-api` | Status HTTP weryfikacji (oczekiwany `202`) oraz treść odpowiedzi |

**Typowe objawy**

- **HTTP 4xx/5xx:** `get()` / `post()` zwracają `Response`. Sprawdź status, treść odpowiedzi i autoryzację. `ensure_success()` zgłasza `HttpStatusError` dla nieprawidłowego statusu.
- **Timeout / `ApiError`:** sprawdź timeout, dostępność adresu i łańcuch wyjątków (`__cause__`). Klient opakowuje błędy transportowe w `ApiError`.
- **Nie zarejestrowano oczekiwania:** sprawdź odpowiedź rejestracji MockServer i jego logi.
- **`/mockserver/verify` nie zwrócił `202`:** sprawdź, czy rzeczywiste żądanie odpowiada zarejestrowanemu oczekiwaniu i czy zostało wysłane.

**Zmienne środowiskowe i markery**

- `LAB_FW_API_TOKEN` — sprawdź, czy token istnieje i jest poprawny.
- `http://mock-api:1080` — adres MockServer z kontenera `tests`; w Compose używaj nazwy usługi `mock-api`.
- `LAB_FW_BASE_URL` — nie ustawiaj globalnie dla Compose bez potrzeby; zwykłe testy korzystają z własnej konfiguracji.
- `@pytest.mark.compose` — marker testów integracyjnych wymagających MockServer.
- Na laptopie z Avast użyj `DOCKER_TARGET=local`, jeśli wymagany jest odpowiedni certyfikat.

**Szybki schemat:** test nie przeszedł → przeczytaj traceback → ustal, czy to odpowiedź HTTP, czy błąd transportowy → w Compose sprawdź `tests`, a następnie `mock-api` → w CI otwórz nieudany krok i pobierz dostępny artefakt.

## Systemy rozproszone: teoria i terminy (lab L1)

Słowniczek na poziomie mid. Gdzie pasuje — powiązanie z `lab_fw` (retry, timeout, `ApiError`, Compose/CI).

### 1. Async communication

Nadawca nie musi czekać na zakończenie całej operacji, zanim pójdzie dalej; wynik może wrócić później. Async **nie równa się** kolejce — kolejka to tylko jeden z mechanizmów.

**QA:** opóźnienia, brak natychmiastowej odpowiedzi, powtórne zdarzenia, błędy tła.

**Przykład:** API zwraca `202 Accepted` (zadanie przyjęte); zamówienie pojawia się później — sprawdzamy i `202`, i późniejszy stan.

### 2. Queue / event / message broker

| Termin | Znaczenie | QA |
|--------|-----------|-----|
| **Queue** | wiadomości czekają na przetwarzanie | brak utraty, poprawna obsługa, brak złych skutków przy retry |
| **Event** | fakt w systemie (np. `OrderCreated`) | pojawia się przy właściwych warunkach z poprawnymi danymi |
| **Message broker** | trasuje wiadomości między serwisami (RabbitMQ, Kafka) | dostawa, routing, błędy, redelivery |

### 3. Retry vs timeout

- **Retry** — czy próbujemy ponownie po przejściowym błędzie (limit prób; nie retryować bez sensu np. typowego `404`).
- **Timeout** — jak długo czekamy (connect / read / overall deadline).

Timeout może prowadzić do retry, ale to różne mechanizmy. Po timeoucie klienta **nie wiesz**, czy serwer dokończył pracę — ślepy retry bez idempotencji jest niebezpieczny.

W `lab_fw`: polityka retry; po wyczerpaniu prób — oczekiwany `ApiError`.

### 4. Timeout

Maks. czas oczekiwania na połączenie, dane lub całą operację (w tym pauzy między retry). Trzy próby po 5 s z pauzami ≠ „tylko 5 s łącznie”.

**QA:** zawieszone wywołania nie blokują w nieskończoność; błędy oczekiwania są przewidywalne (`ApiError` + `__cause__` jak `TimeoutException`).

### 5. Idempotency

Ponowienie operacji nie daje **dodatkowego efektu** względem jednokrotnego wykonania. Nie wymaga identycznego JSON w każdej odpowiedzi (metadane mogą się różnić).

**Idempotency-Key** pomaga serwerowi rozpoznać tę samą operację logiczną. GET/PUT/DELETE zwykle są idempotentne semantyką HTTP; POST zwykle nie (zależy od API).

**Przykład:** ponowne utworzenie płatności z tym samym kluczem nie tworzy drugiej płatności.

### 6. Eventual consistency

Komponenty mogą się chwilowo rozjechać; bez nowych zapisów zbiegają się. **QA:** nie oznaczać defektem każdej krótkiej zwłoki; łapać brak zbieżności w dopuszczalnym czasie. W testach — **polling z deadline**, nie ślepy `sleep`.

### 7. Logs vs metrics vs traces

| | Pytanie | Przykład |
|--|---------|----------|
| **Logs** | co się stało? | `ApiError: HTTP 500` + metoda/URL/czas |
| **Metrics** | jak często / jak dobrze? | error rate, latency p95, retry count |
| **Traces** | gdzie w łańcuchu serwisów? | gateway 20 ms → orders 50 ms → payments 2 s |

### 8. Correlation / Request / Trace ID

Identyfikatory łączące zapisy jednego żądania lub procesu biznesowego. Request ID często = jedno HTTP; Correlation ID obejmuje powiązane kroki; Trace ID — tracing rozproszony. Przy retry polityka może dać nowy Request ID, zachowując Correlation/Trace ID.

### 9. Env vs build („locally green ≠ CI”)

- **Env** — URL, tokeny, timeouty, tryb uruchomienia.
- **Build** — kod, zależności, obraz Dockera.

Sukces lokalnie nie dowodzi sukcesu w CI. Kontroluj: wersje Pythona/zależności, sekrety/env, zawartość obrazu, mocki/serwisy zewnętrzne, komendę pytest w workflow. W tym repo Compose spina usługi; CI sprawdza powtarzalność.

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
