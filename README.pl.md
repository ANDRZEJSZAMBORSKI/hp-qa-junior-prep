# hp-qa-junior-prep

[RU](README.md) · [EN](README.en.md) · **PL**

<!-- readme-preamble -->

Repozytorium **hp-qa-junior-prep** to praktyczny projekt automatyzacji QA w Pythonie. Zawiera pakiet **`lab_fw`** (klient HTTP, warstwa UI, konfiguracja, reporting, plugin pytest), zestaw testów **pytest**, **Docker / Compose**, **GitHub Actions** oraz raporty **Allure**. Typowe przebiegi **nie** wołają produkcyjnego API — kontrakt symulują **MockTransport** i **MockServer**, aby ćwiczyć izolację, integrację i diagnostykę bez zależności od sieci.

Ten dokument to jednocześnie **instrukcja** (polecenia, env, CI) i **podręcznik** (teoria, powiązanie z kodem, typowe błędy). Języki: [RU](README.md) · [EN](README.en.md) · **PL** (ten plik).

### Dla kogo

- Inżynier QA / SDET uruchamiający framework lokalnie i w CI.
- Developer, który chce zrozumieć mocki, równoległy pytest i traceability (TestRail / Jira).

### Efekty

- Wybór poziomu testu: mock in-process vs MockServer w kontenerze vs UI na Grid/Docker.
- Zrozumienie retry, timeout, deadline i idempotency na przykładzie `ApiClient` i `Worker`.
- Badanie awarii: env → build → logs → metrics → trace.
- Allure oraz opcjonalne powiązanie z TestRail i Jira.

### Wymagania

| Składnik | Wersja / uwagi |
|----------|----------------|
| Python | **≥ 3.11** (`pyproject.toml`) |
| Git | klon i ten sam commit co CI |
| Docker Desktop (opcjonalnie) | testy Compose, Grid, obraz Playwright |
| Allure CLI (opcjonalnie) | lokalne `allure serve` |
| TestRail CLI (opcjonalnie) | kanał B w sekcji N2 |

### Mapa sekcji

| Blok | Temat | Kod |
|------|--------|-----|
| **I1–I4** | API, mocki, negatywy, diagnostyka | `tests/mocks_lab/`, `tests/test_compose_api.py`, `src/lab_fw/api/` |
| **L1–L3** | Systemy rozproszone, kolejka/worker, badanie | `src/distributed_lab/`, `tests/distributed_lab/` |
| **M1–M2** | xdist, izolacja, Selenium Grid, UI w Dockerze | `tests/parallel_lab/`, `tests/conftest.py`, profile Compose |
| **N1–N2** | Allure, TestRail, Jira | `src/lab_fw/reporting/`, `tests/test_api_client.py`, `scripts/upload_testrail.sh` |

Proponowana kolejność: **Szybki start → Struktura → I1–I4 → L1 → L2 → L3 → M1 → M2 → N1 → N2**. Sekcje **Docker** i **GitHub Actions** warto mieć pod ręką przy każdym uruchomieniu.

### Spis treści

1. [Szybki start](#szybki-start-lokalnie)
2. [Struktura](#struktura)
3. [Zmienne środowiskowe](#zmienne-środowiskowe)
4. [Markery pytest](#markery-pytest)
5. [Docker](#docker)
6. [GitHub Actions](#github-actions)
7. [I1 — schemat API](#schemat-interakcji-api-i1) (w tym I2–I4)
8. [L1 — słownik](#systemy-rozproszone-teoria-i-terminy-l1)
9. [L2 — kolejka i worker](#l2--kolejka-retry-timeout-deadline-idempotency)
10. [L3 — badanie awarii](#l3--badanie-awarii-checklista)
11. [M1 — równoległość](#m1--równoległe-uruchamianie-i-izolacja-zasobów)
12. [M2 — Grid i UI](#m2--zdalna-przeglądarka-selenium-grid-i-ui-w-dockerze)
13. [N1 — Allure](#n1--raporty-allure)
14. [N2 — TestRail i Jira](#n2--jira--i-testrail)
15. [Allure (skrót)](#allure-skrót)
16. [Dokumentacja modułów](#dokumentacja-modułów)

### Jak czytać rozdziały

Na początku sekcji jest **O tym rozdziale**: cel, pliki w repo, samokontrola. Potem tabele i polecenia. Przy padnięciu testu — najpierw [I4](#diagnostyka-padających-testów-i4), przy problemach infrastruktury — [L3](#l3--badanie-awarii-checklista).

## Szybki start (lokalnie)

<!-- readme-chapter:quickstart -->
### O tym rozdziale

Najkrótsza ścieżka od czystej maszyny do zielonego przebiegu unit/API bez przeglądarki i MockServer — ten sam wycinek co workflow **tests** na GitHubie (bez markera `compose`).

### Krok po kroku

1. Sklonuj repo, wejdź do katalogu głównego.
2. Utwórz venv na **Pythonie 3.11+** i aktywuj.
3. `pip install -e ".[dev]"` — editable `lab-fw` oraz pytest, xdist, allure, playwright, selenium, filelock.
4. Uruchom szybki suite (polecenie poniżej). Oczekuj setek passed; kilka minut na laptopie.

### Filtr markerów

`-m "not ui and not selenium and not compose"` pomija testy wymagające prawdziwej przeglądarki lub kontenera `mock-api`. Do pierwszego sukcesu nie potrzebujesz Dockera ani `playwright install`.

### UI (osobno)

Playwright i Selenium wymagają przeglądarki. Playwright: `playwright install chromium`. Selenium 4 na Windows często sam pobiera Chrome (Selenium Manager).

### Samokontrola

| Pytanie | Gdzie sprawdzić |
|---------|-----------------|
| Editable install? | `python -m pip show lab-fw` |
| Działa xdist? | w output pytest jest `[gw0]` przy `-n auto` |
| Dlaczego brak compose? | brak MockServer — sekcja Docker |

### Typowe problemy

- **Zła wersja Pythona** — nowe venv 3.11+.
- **Import errors** — venv aktywne? `pip install -e ".[dev]"`?
- **Playwright** — nie uruchamiaj `-m ui` przed `playwright install`.


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

<!-- readme-chapter:structure -->
### O tym rozdziale

Mapa repozytorium: kod frameworka, scenariusze pytest, Docker i CI.

### Drzewo (główne ścieżki)

| Path | Zawartość |
|------|-----------|
| `src/lab_fw/api/` | `ApiClient`, retry, auth, błędy |
| `src/lab_fw/ui/` | Playwright / Selenium, page objects |
| `src/lab_fw/config/` | `Settings`, env |
| `src/lab_fw/reporting/` | dekoratory Allure |
| `src/lab_fw/pytest_plugin/` | hooki, markery |
| `src/distributed_lab/` | `Job`, `Worker`, kolejka (L2) |
| `tests/mocks_lab/` | mocki (I2) |
| `tests/distributed_lab/` | L2/L3 |
| `tests/parallel_lab/` | M1 |
| `scripts/` | upload TestRail |
| `categories.json` | Allure Categories |
| `.github/workflows/` | **tests**, **CI** |

### Dwa poziomy

- **`lab_fw`** — biblioteka importowana przez testy.
- **`tests/`** — katalog wzorców i regresji.

### Samokontrola

Po `pip install -e ".[dev]"` polecenie `import lab_fw` z katalogu głównego musi działać.


| Ścieżka | Przeznaczenie |
|---------|---------------|
| `src/lab_fw/` | framework (api, ui, config, reporting, plugin pytest) |
| `tests/` | suite pytest |
| `Dockerfile` | multi-stage: `local` (CA Avast) / `ci` / `playwright` |
| `docker-compose.yml` | `mock-api` + `tests`; profile `selenium`, `playwright` |
| `.github/workflows/tests.yml` | unit/API na runnerze (bez UI/compose) |
| `.github/workflows/ci.yml` | Compose: API → Selenium Grid → Playwright w Dockerze |

## Zmienne środowiskowe

<!-- readme-chapter:env -->
### O tym rozdziale

Konfiguracja przez env i `Settings`. Większość testów MockTransport **nie wymaga** prawdziwego tokenu.

### Kolejność

1. Wartość w teście/fixture.
2. Env (`LAB_FW_*`).
3. Domyślne w kodzie.

### Praktyka

- Lokalnie token może być pusty.
- W CI workflow **tests** token ze Secrets jest wymagany.
- Testy Compose: `http://mock-api:1080` w `Settings`.

### Samokontrola

```bash
python -c "from lab_fw.config import get_settings; s=get_settings(); print(s.base_url, s.timeout_s)"
```


| Env | Przeznaczenie |
|-----|---------------|
| `LAB_FW_BASE_URL` | API base URL (domyślnie `https://example.com`) |
| `LAB_FW_UI_BASE_URL` | UI base URL (domyślnie the-internet.herokuapp.com) |
| `LAB_FW_API_TOKEN` | opcjonalny Bearer token |
| `LAB_FW_TIMEOUT_S` / `LAB_FW_UI_TIMEOUT_S` | timeouty |
| `LAB_FW_LOG_LEVEL` | poziom logów |
| `SELENIUM_REMOTE_URL` | URL Selenium Grid (`webdriver.Remote`); brak → lokalny Chrome |
| `DOCKER_TARGET` | target build Compose: `ci` (domyślnie) lub `local` (CA Avast) |

Sekret CI: GitHub → Settings → Secrets → `LAB_FW_API_TOKEN`.

## Markery pytest

<!-- readme-chapter:markers -->
### O tym rozdziale

Markery wybierają podzbiory testów i sterują CI. **Nie** uruchamiają infrastruktury.

### CI

| Workflow | Filtr | Efekt |
|----------|-------|--------|
| **tests** | bez ui/selenium/compose | szybki runner |
| **CI** | często z compose | wymaga `mock-api` |

### Ścieżki

- `distributed_lab` — L2/L3.
- `parallel_lab` — M1.
- `reporting` — Allure.

### Samokontrola

`pytest --markers` — opisy w `pyproject.toml`.


| Marker | Znaczenie |
|--------|-----------|
| `smoke` / `api` / … | zwykłe szybkie testy |
| `ui` | prawdziwy Playwright |
| `selenium` | prawdziwy Selenium |
| `compose` | wymaga usługi `mock-api` z Compose |
| `parallel_lab` | ćwiczenia M1 (xdist, pliki, lock) |
| `distributed_lab` | ćwiczenia L2/L3 |
| `serial` | wspólny stan (module-scoped UI/Selenium); nie uruchamiać z `-n` |
| `reporting` | testy warstwy Allure / `lab_fw.reporting` |

## Docker

<!-- readme-chapter:docker -->
### O tym rozdziale

Docker odtwarza CI lokalnie: obraz `tests`, MockServer, opcjonalnie Grid/Playwright.

### Model

1. Obraz **ci** — pytest w Linuxie.
2. Sieć Compose — `mock-api` po DNS.
3. Profile — UI opcjonalnie.

### `DOCKER_TARGET=local`

MITM — target **local** + `avast-root.crt` lokalnie.

### Samokontrola

`docker compose up --build --abort-on-container-exit tests`

### Błędy

- Compose bez `mock-api`.
- Mylenie CMD obrazu z workflow **tests**.


### Obrazy (`Dockerfile`)

- **`ci`** — na GitHub / Linux bez firmowego MITM
- **`local`** — kopiuje `avast-root.crt` (plik lokalny, nie w git)
- **`playwright`** — obraz bazowy Microsoft Playwright z Chromium (profile `playwright` w Compose)

`Dockerfile.local` i `avast-root.crt` są w `.gitignore`.

```bash
docker build --target ci -t hp-qa-junior-prep:ci .
docker run --rm -e LAB_FW_API_TOKEN=ci-demo-token hp-qa-junior-prep:ci

docker build --target local -t hp-qa-junior-prep:local .
docker run --rm -e LAB_FW_API_TOKEN=ci-demo-token hp-qa-junior-prep:local
```

CMD obrazu: `pytest -m "not ui and not selenium"` — **obejmuje** testy `compose`, gdy dostępny jest `mock-api`.

### Docker Compose

**Domyślny przebieg (API, compose, parallel_lab — bez UI):**

```bash
docker compose up --build --abort-on-container-exit tests
docker compose down

DOCKER_TARGET=local docker compose up --build --abort-on-container-exit tests
```

**Profile `selenium`** — Grid + testy w obrazie `ci`:

```bash
docker compose --profile selenium run --build --rm selenium-tests
docker compose --profile selenium run --build --rm selenium-tests-serial
docker compose --profile selenium down
```

- `selenium` — `selenium/standalone-chrome`, porty `4444` (WebDriver), `7900` (noVNC)
- w `selenium-tests*` ustawione jest `SELENIUM_REMOTE_URL=http://selenium:4444`

**Profile `playwright`** — UI Playwright w obrazie `playwright`:

```bash
docker compose --profile playwright run --build --rm playwright-tests
docker compose --profile playwright run --build --rm playwright-tests-serial
```

Usługi domyślne (bez profile): `mock-api` (`:1080`) + `tests` (`${DOCKER_TARGET:-ci}`, CMD z Dockerfile).

`LAB_FW_BASE_URL` **nie** jest ustawiane globalnie w compose (starsze testy oczekują `example.com` / MockTransport). Testy compose wołają `http://mock-api:1080` wprost.

## GitHub Actions

<!-- readme-chapter:gha -->
### O tym rozdziale

Dwa pipeline: szybki runner i pełna integracja w Dockerze.

### tests.yml

- pytest bez ui/selenium/compose, artifact Allure (wycinek).

### ci.yml

- Pełny łańcuch Compose + Selenium + Playwright.

### Nauka

Logi joba → artifact → porównaj polecenie pytest z README.


| Workflow | Co robi |
|----------|---------|
| **tests** | `pip install` + `pytest -m "not ui and not selenium and not compose"` + artefakt Allure |
| **CI** | kroki: `tests` → `down` → Selenium → Playwright; `DOCKER_TARGET=ci`; artefakt **`allure-results`** (pełny Docker) |

| Gdzie | mock-api? | Testy compose |
|-------|-----------|---------------|
| **CI** / lokalny compose | tak | uruchamiane |
| workflow **tests** | nie | wykluczone (`not compose`) |

## Schemat interakcji API (I1)

<!-- readme-chapter:i1 -->
### O tym rozdziale (I1–I4)

**Integracja / API**: test klienta HTTP bez produkcji i kiedy mock w kontenerze.

| Część | Temat |
|-------|--------|
| **I1** | MockTransport vs MockServer |
| **I2** | Strategia mocków |
| **I3** | 401, timeout |
| **I4** | Logi i CI |

### Pliki

- `src/lab_fw/api/client.py`
- `tests/test_compose_api.py`

### Ćwiczenie

`pytest tests/mocks_lab -q` vs `docker compose up … tests`.


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

### Strategia mocków (I2)

#### O podrozdziale I2

Porównanie dwóch szwów podmiany HTTP: **MockTransport** w procesie vs **MockServer** w kontenerze.

**Studium:** [tests/mocks_lab/](tests/mocks_lab/README.pl.md) i `tests/test_compose_api.py`.

**Samokontrola:** dlaczego DI `transport=` jest lepsze niż ciągłe `patch('httpx.Client')`?

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

### Negatywne scenariusze integracyjne (I3)

#### O podrozdziale I3

Testy negatywne sprawdzają **kontrakt błędów**: 401 vs timeout transportu. Rozróżniaj HTTP od `ApiError` i `__cause__`.

**Praktyka:** przeczytaj `ApiClient.get` / `ensure_success` w `src/lab_fw/api/`.

W `tests/test_compose_api.py` (marker `compose`, ten sam `reset_mockserver`):

| Test | MockServer | Co sprawdzamy |
|------|------------|---------------|
| `test_mock_api_auth_fail` | `GET /protected` → **401** + JSON `error` | klient dostaje status/ciało/Content-Type bez prawdziwego IdP |
| `test_mock_api_timeout` | `GET /slow` z `delay` 1000 ms, `timeout_s=0.2` | `ApiError`; `__cause__` to `ReadTimeout` ⊂ `TimeoutException` ⊂ `HTTPError`; potem `/mockserver/verify` → **202** |

Polityka klienta: przy 4xx/5xx `get`/`post` **zwracają** `Response` (opcjonalnie `ensure_success` → `HttpStatusError`). Błędy transportu (timeout itd.) zawsze jako `ApiError`.

### Diagnostyka padających testów (I4)

#### O podrozdziale I4

**Mapa miejsc** przy czerwonym pytest. Łącz z [L3](#l3--badanie-awarii-checklista).

**Ćwiczenie:** zepsuj expectation w compose i sprawdź `/mockserver/verify` (202 vs nie).

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

## Systemy rozproszone: teoria i terminy (L1)

<!-- readme-chapter:l1 -->
### O tym rozdziale

**L1** — fundament pod L2/L3: terminy z logów produkcyjnych i rozmów kwalifikacyjnych.

### Nauka

Czytaj 1–9, mapuj na `lab_fw`, potem L2.

### Samokontrola

retry ≠ timeout; idempotency ≠ ten sam JSON.


### 1. Async communication

<!-- l1-deep:1 -->
#### O punkcie 1 — komunikacja asynchroniczna

**Sens:** kod wywołujący nie blokuje się do końca przetwarzania; wynik obsługuje później inny komponent.

**W repozytorium:** kolejka `InMemoryQueue` + `Worker.run_once()` — wrzucasz `Job`, HTTP wykona się przy następnym `run_once`, a nie w momencie `put`.

```python
# src/distributed_lab/queue_worker.py (idea)
queue.put(job)
worker.run_once()  # jeden job → HTTP przez ApiClient
```

**QA:** testuj osobno „przyjęte do przetwarzania” i „stan końcowy”; nie traktuj tego jak fire-and-forget bez asercji.

**Sprawdzenie:** `pytest tests/distributed_lab/test_queue_worker.py -q`

### 2. Queue / event / message broker

<!-- l1-deep:2 -->
#### O punkcie 2 — kolejka / zdarzenie / broker

**W repozytorium:** uproszczona **kolejka** — FIFO na `deque`, typowany `Job` (`parse_job` → `SchemaError` przy złym payloadzie).

```python
# src/distributed_lab/queue_worker.py
class InMemoryQueue:
    def put(self, job: Job) -> None: ...
    def get(self) -> Job | None: ...
```

**Zdarzenie** w produkcji to fakt domenowy (`OrderCreated`); tutaj odpowiednik to dict joba walidowany do modelu.

**QA:** po `put` job nie ginie; skutki ponownej dostawy — punkt 5 (idempotency).

**Sprawdzenie:** `pytest tests/distributed_lab/test_queue_worker.py -k queue -q`

### 3. Retry vs timeout

<!-- l1-deep:3 -->
#### O punkcie 3 — retry a timeout

**Retry** odpowiada na pytanie „czy powtórzyć po błędzie”; **timeout** — „jak długo czekać na jedną próbę”. Po timeoutie wynik po stronie serwera jest **nieznany** — ślepy retry POST jest niebezpieczny bez idempotency.

**Polityka w kodzie** (`src/lab_fw/api/retry_policy.py`):

```python
def should_retry(exc: ApiError) -> bool:
    # GET + 429/503 lub GET + błąd transportu → True
    # POST → False
```

**Orkiestracja:** `lab_fw.core.retry.retry_call` woła `should_retry` między próbami.

**Sprawdzenie:** `pytest tests/test_api_retry_policy.py tests/distributed_lab/test_l3_investigation.py -q`

### 4. Timeout

<!-- l1-deep:4 -->
#### O punkcie 4 — timeout

**Warstwy timeoutu w repozytorium:**

| Warstwa | Gdzie |
|---------|--------|
| Klient HTTP | `Settings.timeout_s` → `ApiClient` |
| Negatyw Compose | `timeout_s=0.2` vs opóźnienie 1000 ms w MockServer (`tests/test_compose_api.py`) |
| Job / worker | `Job.timeout`, `Job.deadline_s`, `Worker.deadline_w` → `JobDeadlineExceeded` |

```python
# Worker.execute — minimum z timeoutu joba i pozostałego deadline
timeout = min(job.timeout, remaining, remaining_worker)
```

**QA:** asercja na typ błędu: `ApiError` z `__cause__` typu `ReadTimeout`, nie tylko „padło”.

**Sprawdzenie:** `pytest tests/test_compose_api.py::test_mock_api_timeout tests/distributed_lab/test_timeout.py -q`

### 5. Idempotency

<!-- l1-deep:5 -->
#### O punkcie 5 — idempotency

**Nagłówek na wire** (bez mutacji modelu joba):

```python
# src/distributed_lab/queue_worker.py
if job.idempotency_key is not None:
    kwargs["headers"]["Idempotency-Key"] = job.idempotency_key
```

**Serwer testowy** w `tests/distributed_lab/test_timeout.py`: powtórny POST z tym samym kluczem nie zwiększa `received_requests`.

**Polityka retry:** POST **nie** jest retryowany w `should_retry` / workerze — ochrona przed podwójnym efektem ubocznym.

**Sprawdzenie:** `pytest tests/distributed_lab/test_timeout.py -q -k idempotency`

### 6. Eventual consistency

<!-- l1-deep:6 -->
#### O punkcie 6 — eventual consistency

**Idea:** stany systemów mogą chwilowo się różnić; test czeka na zgodność z **deadline**, a nie na stały `sleep`.

**W repozytorium:** worker sprawdza pozostały czas przez `_remaining_time` przed i po HTTP; warstwa UI używa jawnych waitów (`PlaywrightWait` / `SeleniumWait`) zamiast ślepej pauzy.

**Wzorzec QA:**

```python
# antywzorzec: time.sleep(5)
# lepiej: wait z timeoutem ze settings (ui_timeout_s / deadline joba)
```

**Sprawdzenie:** `pytest tests/test_playwright_wait.py tests/test_selenium_wait.py -q`

### 7. Logs vs metrics vs traces

<!-- l1-deep:7 -->
#### O punkcie 7 — logi, metryki, trace

| Sygnał | Przykład w repozytorium |
|--------|-------------------------|
| **Logi** | `INFO lab_fw.api`, `WARNING lab_fw.core.retry` przy retry |
| **Metryki** | ręczne liczniki L3: `http_requests`, `503_count` |
| **Trace** | brak pełnego OTel; jest wire ID `X-Request-ID` (pkt 8) |

**Praktyka L3:** `caplog` łapie dwa WARNING przed udanym retry 503→200.

**Sprawdzenie:** `pytest tests/distributed_lab/test_l3_investigation.py -q`

### 8. Correlation / Request / Trace ID

<!-- l1-deep:8 -->
#### O punkcie 8 — correlation / Request / Trace ID

**W repozytorium:** job przekazuje nagłówki bez zmian — testy ustawiają `X-Request-ID`:

```python
# tests/distributed_lab/test_timeout.py — nagłówki joba na HTTP
headers={"X-Request-ID": "req-123"}
```

**Retry:** każda próba GET może powtórzyć ten sam `Idempotency-Key`; polityka Request ID zależy od API (tu — to, co włożysz w job).

**QA:** przeszukaj repo: `grep -Rni "X-Request-ID" src tests`

**Sprawdzenie:** `pytest tests/distributed_lab/test_timeout.py -q -k request`

### 9. Env vs build („locally green ≠ CI”)

<!-- l1-deep:9 -->
#### O punkcie 9 — env a build

**Env (przykład L3):** lokalnie `LAB_FW_API_TOKEN` może być pusty; w workflow CI **tests** secret jest **wymagany**.

**Build:** `git rev-parse HEAD`, editable `lab-fw`, target obrazu Docker `ci` vs `local` (Avast CA).

```bash
python -c "import os; print(os.getenv('LAB_FW_API_TOKEN', 'MISSING'))"
docker compose config | head
```

**QA:** pada tylko w CI → najpierw porównaj env i polecenia pytest w `.github/workflows/`, nie „przepisuj test”.

**Sprawdzenie:** przeczytaj `tests/distributed_lab/test_l3_investigation.py` (sekcje env/build).

## L2 — kolejka, retry, timeout, deadline, idempotency

<!-- readme-chapter:l2 -->
### O tym rozdziale

**L2** — kolejka → worker → HTTP z retry i limitami czasu.

### Architektura

Job → kolejka → Worker → ApiClient.

### Samokontrola

POST — jedna próba przy timeout; GET retry przy 503.


Implementacja i testy do [L1](#systemy-rozproszone-teoria-i-terminy-l1): kolejka in-memory → worker → HTTP przez `ApiClient` z `lab_fw`, z polityką retry i limitami czasu.

**Kod:** `src/distributed_lab/queue_worker.py`  
**Testy:** `tests/distributed_lab/` (marker `@pytest.mark.distributed_lab`)

### Komponenty

| Komponent | Rola |
|-----------|------|
| `Job` | Zadanie: `method`, `path`, opcjonalnie `timeout`, `deadline_s`, `payload`, `headers`, `idempotency_key` |
| `parse_job` | Walidacja dict → `Job`; błędy schematu → `SchemaError` |
| `InMemoryQueue` | FIFO na `deque`; `put` przyjmuje tylko `Job` |
| `Worker` | `run_once()` — jedno zadanie; `execute()` — jedno wywołanie HTTP |

Worker buduje kwargs klienta: `json` z `payload`, kopia `headers`, a gdy jest `idempotency_key` — nagłówek `Idempotency-Key` (bez mutacji modelu job).

### Retry i metoda HTTP

W `run_once` jest `retry_call` (do 3 prób) i `lab_fw.api.retry_policy.should_retry`:

- **GET:** retry przy `429` / `503` i błędach transportowych (`ConnectError`, `ReadTimeout`, …);
- **POST:** **brak** retry (nawet przy `429`/`503` lub timeout) — mniejsze ryzyko podwójnego efektu bez idempotencji po stronie serwera.

Po wyczerpaniu prób lub przy statusie bez retry — `ApiError` / `HttpStatusError` (przez `ensure_success`).

### Timeout vs deadline

| Mechanizm | Gdzie | Znaczenie |
|-----------|--------|-----------|
| **Timeout** | `Settings.timeout_s`, `Job.timeout` | Ile czekać na jedno wywołanie HTTP (connect/read) |
| **Job deadline** | `Job.deadline_s` | Budżet czasu na job (w tym retry); koniec → `JobDeadlineExceeded` |
| **Worker deadline** | `Worker(..., deadline_w=...)` | Budżet sesji workera; koniec → `WorkerDeadlineExceeded` |

Timeout żądania to **minimum** z job timeout, pozostałego job deadline i pozostałego worker deadline. Po `ApiError` worker ponownie sprawdza deadline — końcowy błąd może być deadline, a nie ostatni błąd HTTP.

### Idempotency (serwer HTTP do nauki)

W `tests/distributed_lab/test_timeout.py` — `WorkerTestHandler`: powtórny POST z tym samym `Idempotency-Key` **nie dodaje** drugiego wpisu do `received_requests`, ale zwraca dane pierwszego żądania. Testy obejmują:

- JSON i nagłówki (w tym `X-Request-ID`) na prawdziwym HTTP;
- brak `Idempotency-Key`, gdy pole nie jest ustawione;
- POST przy timeout — jedna próba, klucz na wire;
- dwa joby, ten sam klucz — `server.calls == 2`, `len(received_requests) == 1`;
- GET retry (503→200) — ten sam `Idempotency-Key` przy każdej próbie.

### Uruchomienie

```bash
# distributed_lab (L2)
pytest -m distributed_lab -q

# tylko kolejka/worker (bez wolnego serwera HTTP)
pytest tests/distributed_lab/test_queue_worker.py -q

# timeout, deadline, idempotency na lokalnym serwerze HTTP
pytest tests/distributed_lab/test_timeout.py -q
```

Docker / MockServer do L2 **nie są potrzebne** — wystarczy venv i `pip install -e .`.

### Gdy test pada

1. Traceback: `JobDeadlineExceeded` / `WorkerDeadlineExceeded` vs `ApiError` i `__cause__` (`ReadTimeout`, `ConnectError`, …).
2. Liczniki prób w MockTransport lub `server.request_counts` / `received_requests` w testach slow-server.
3. Metoda job: POST nie powinien dawać trzech prób przy domyślnej polityce retry.

## L3 — badanie awarii (checklista)

<!-- readme-chapter:l3 -->
### O tym rozdziale

**L3** — checklista **Env → Build → Logs → Metrics → Trace**.

### I4 vs L3

I4 — gdzie szukać; L3 — kolejność analizy.

### Praktyka

`test_l3_investigation.py`.


Systematyczna diagnostyka w pięciu obszarach: **Env → Build → Logs → Metrics → Trace**. Praktyka: zachowanie **retry**, logi przez `caplog` oraz ręczne **liczniki badania** (*investigation counters*).

**Testy:** `tests/distributed_lab/test_l3_investigation.py` (marker `@pytest.mark.distributed_lab`)

**Zob. też:** [I4 — diagnostyka padających testów](#diagnostyka-padających-testów-i4); [L2](#l2--kolejka-retry-timeout-deadline-idempotency) (kolejka, worker, retry, deadline). L3 — kolejność Env → Build → Logs oraz scenariusze retry z `caplog`.

### 1. Env — zmienne środowiskowe

Sprawdzenie lokalne (przykład):

```bash
python -c "import os; print('LAB_FW_API_TOKEN:', 'SET' if os.getenv('LAB_FW_API_TOKEN') else 'MISSING'); print('LAB_FW_BASE_URL:', os.getenv('LAB_FW_BASE_URL', '<unset>')); print('LAB_FW_LOG_LEVEL:', os.getenv('LAB_FW_LOG_LEVEL', '<unset>'))"
```

Gdy zmienne nie są ustawione, `get_settings()` stosuje domyślne: `base_url=https://example.com`, `timeout_s=5.0`, `log_level=INFO`, `api_token=None`.

**Lokalnie vs CI:** workflow **tests** w GitHub Actions ustawia `LAB_FW_API_TOKEN` ze Secrets i weryfikuje, że nie jest pusty. Brak tokenu lokalnie przy L3 jest OK z MockTransport; w CI env jest inny — typowy przypadek **local ≠ CI**.

### 2. Build — stan projektu

| Sprawdzenie | Po co |
|-------------|--------|
| `git rev-parse --short HEAD` | ten sam commit co w CI |
| `python -m pip show lab-fw` | wersja pakietu, editable install |
| `git status` | niezacommitowane zmiany vs czysty build |

### 3. Logs — lab retry

`httpx.MockTransport` + `Worker` + `ApiClient`. Dwa scenariusze:

| Scenariusz | Zachowanie | Asercje |
|------------|------------|---------|
| Udane retry | 503, 503, 200 | 3 próby; 2× `WARNING` z `lab_fw.core.retry`; odpowiedź `{"ok": true}` |
| Wyczerpanie (`exhausted`) | 503 × 3 | 3 próby; 2× `WARNING`; `HttpStatusError`; status/method/path |

Logi: `INFO` — `lab_fw.api`; `WARNING` — `lab_fw.core.retry` przed kolejną próbą. Trzecia porażka nie musi dawać trzeciego WARNING.

### 4. Metrics — liczniki badania

W repozytorium nie ma wbudowanego Prometheusa/metryk. Dla scenariusza „same 503” zapisuj **ręczne liczniki z testu**:

- `http_requests = 3`
- `503_count = 3`
- `retries_after_first = 2`

To nie są metryki produkcyjne (brak error rate / p95 w runtime). Szukanie w kodzie: `grep -RniE "prometheus|metrics|histogram|counter|p95" src tests pyproject.toml`.

### 5. Trace — korelacja

Szukanie ID: `grep -RniE "X-Request-ID|Correlation-ID|request_id" src tests`. Testy L2 sprawdzają `X-Request-ID: req-123`. To **identyfikator na wire**, nie pełny tracing rozproszony (brak auto Trace ID / spanów między serwisami).

### Jak łączą się I4, L3 i L2

| Etap | Pytanie |
|------|---------|
| **I4** | Gdzie szukać? (pytest, Compose, mock-api, CI) |
| **L3** | W jakiej kolejności? (Env → Build → Logs → Metrics → Trace) |
| **L2** | Kolejka, worker, deadline, idempotency |
| **L3 (retry)** | retry + `caplog` + liczniki badania |


### Uruchomienie

```bash
pytest tests/distributed_lab/test_l3_investigation.py -v
```

### Ograniczenia L3

`MockTransport` — bez prawdziwej sieci i bez Docker/MockServer. Automatyczne metryki i platforma tracing end-to-end nie wchodzą w zakres L3.

## M1 — równoległe uruchamianie i izolacja zasobów

<!-- readme-chapter:m1 -->
### O tym rozdziale

**M1** — pytest-xdist i ryzyko współdzielonych zasobów.

### Idea

Równoległość dla testów niezależnych; MockServer/pliki — `loadgroup` lub `@serial`.

### Kod

`tests/conftest.py`, `tests/parallel_lab/`.


`pytest-xdist` w tym repozytorium: współdzielone zasoby (MockServer, pliki, przeglądarka), `xdist_group`, `loadgroup` i artefakty per worker.

### Strategie izolacji

| Współdzielony zasób | Strategia | Konfiguracja |
|---|---|---|
| MockServer w Docker Compose | Grupowanie konfliktujących testów na jednym workerze | Marker `@pytest.mark.xdist_group(name="mockserver")` w `tests/conftest.py` dla testów `@pytest.mark.compose`; uruchomienie z `--dist loadgroup` |
| Jeden lokalny browser bez Grid | Sekwencyjne wykonanie konfliktujących testów | Wspólna grupa + `--dist loadgroup` |
| Wspólny plik raportu | Osobny plik na worker | `worker_id` w nazwie pliku lub `tmp_path` |
| Zasób tworzony na test | Utworzenie i cleanup na test | Fixture pytest z poprawnym teardown |

Zwykły `threading.Lock` nie synchronizuje wspólnego pliku między procesami: workery xdist to osobne procesy. Gdy wspólny plik jest konieczny, potrzebna jest blokada międzyprocesowa. Dla artefaktów testowych prostsze są osobne pliki.

### Compose i MockServer

Testy Compose używają jednej instancji MockServer. Gdy kilka testów jednocześnie zmienia oczekiwania lub resetuje stan, mogą na siebie wpływać.

W `tests/conftest.py` hook `pytest_collection_modifyitems` przypisuje testom z markerem `compose` marker `@pytest.mark.xdist_group(name="mockserver")`.

#### Dlaczego ważne jest `tryfirst=True`

Przy `--dist loadgroup` xdist grupuje testy według markera `xdist_group`.

Podczas kolekcji hook `pytest_collection_modifyitems` w `tests/conftest.py` dodaje `xdist_group(name="mockserver")` testom oznaczonym `compose`. Aby grupowanie działało, marker musi być ustawiony zanim logika xdist zbuduje plan dla schedulera.

Po stronie workera xdist używa `xdist_group` do sufiksu w `nodeid`, np. `@mockserver`. Gdy marker pojawi się za późno, controller może dostać identyfikatory bez tego sufiksu. Wtedy `LoadGroupScheduling` nie połączy konfliktujących testów w jedną grupę i mogą iść równolegle na różnych workerach.

W projekcie używane jest `@pytest.hookimpl(tryfirst=True)` — patrz `tests/conftest.py`. Podnosi priorytet hooka, aby marker grupy był ustawiony przed przetwarzaniem grupowania przez xdist.

Sam `tryfirst=True` nie blokuje dostępu do zasobu: izolację daje poprawne grupowanie i konfiguracja uruchomienia.

#### `loadgroup` a `loadscope`

- `--dist load` — rozdziela pojedyncze testy między workery; dla testów niezależnych.
- `--dist loadscope` — trzyma testy jednego modułu lub klasy na jednym workerze. Gdy wszystkie konfliktujące testy Compose są w jednym module, to może wystarczyć.
- `--dist loadgroup` — łączy testy z tym samym `xdist_group`, także z różnych modułów. Elastyczniejsze dla wspólnej grupy zasobów.

W `Dockerfile` projektu jest już `-n auto` i `--dist loadgroup`.

#### Rola `reset_mockserver`

Fixture `reset_mockserver` w `tests/test_compose_api.py` resetuje MockServer przed i po każdym teście.

To utrzymuje czysty stan między testami wykonywanymi sekwencyjnie. Nie zastępuje grupowania: przy równoległej pracy dwóch testów na jednym MockServer reset jednego może zepsuć drugi.

### Weryfikacja

#### 1. Uruchomienie Compose

```bash
docker compose up --build --abort-on-container-exit tests
```

Uruchamia `mock-api` i kontener `tests` (API / compose / parallel_lab, bez UI).

#### 2. Sprawdzenie grupowania testów Compose

W kontenerze `tests`:

```bash
docker compose run --rm tests pytest tests/test_compose_api.py -vv -n auto --dist loadgroup
```

Uruchamia testy z `tests/test_compose_api.py` z verbose i scheduleringiem `loadgroup`.

Szukaj trzech sygnałów:

- Na początku sesji: `scheduling tests via LoadGroupScheduling`.
- W liniach testów: sufiks grupy, np. `tests/test_compose_api.py::test_mock_api_users@mockserver`.
- Wszystkie cztery testy Compose na tym samym workerze, np. `[gw0]`. Numer może być inny; ważne, że cała grupa na jednym workerze.

Przy uruchomieniu przez Compose serwis `mock-api` musi być dostępny z kontenera testów pod `http://mock-api:1080`.

#### 3. Podział uruchomień w CI

Testy zwykłe i Compose są rozdzielone:

- `.github/workflows/tests.yml` — `-n auto`, bez markerów `ui`, `selenium`, `compose`.
- `.github/workflows/ci.yml` — najpierw serwis `tests`, potem profile `selenium` i `playwright` (patrz [M2](#m2--zdalna-przeglądarka-selenium-grid-i-ui-w-dockerze)).
- `Dockerfile` — `-n auto --dist loadgroup` dla pytest w kontenerze.

CI oddziela główny suite od testów wymagających współdzielonego MockServer.

### Praktyka: `parallel_lab`

Kod: `tests/parallel_lab/test_parallel_resources.py`, marker `@pytest.mark.parallel_lab` (patrz `pyproject.toml`). Testy z lockiem wymagają `filelock` w `[project.optional-dependencies]` (`dev` / `dev_slim`).

| Temat | Testy (idea) |
|---|---|
| Osobny plik na worker (`PYTEST_XDIST_WORKER`) | `test_shared_file_write_read`, `test_worker_specific_files_are_isolated` |
| Izolacja przez `tmp_path` | `test_tmp_path_creates_isolated_temp_file`, `test_tmp_path_is_unique_for_each_test` |
| Wspólny plik + `FileLock` pod xdist | `test_shared_file_access_with_file_lock`, `test_shared_file_access_is_serialized` |
| Wyścig bez locka (multiprocessing, powtarzalnie) | `test_shared_file_race_condition_is_reproducible` |
| Lock między procesami | `test_file_lock_prevents_shared_file_race` |

Uruchomienie:

```bash
pytest tests/parallel_lab -m parallel_lab -v
pytest tests/parallel_lab -m parallel_lab -n 2 -v
```

Pliki `shared_report*.txt` w katalogu laby to lokalne artefakty; nie commituj ich (patrz `.gitignore`). Pełny suite w Dockerze (`Dockerfile` CMD) obejmuje `parallel_lab` razem z testami bez `ui` / `selenium`.

Równoległy przebieg przyspiesza niezależne testy; współdzielone zasoby wymagają grupowania (`loadgroup`), osobnych plików lub `FileLock` oraz poprawnego teardown. Zob. [I4](#diagnostyka-padających-testów-i4), [L2](#l2--kolejka-retry-timeout-deadline-idempotency), [L3](#l3--badanie-awarii-checklista).

## M2 — zdalna przeglądarka (Selenium Grid) i UI w Dockerze

<!-- readme-chapter:m2 -->
### O tym rozdziale

**M2** — UI: Grid, runner pytest, parallel vs **serial**.

### Samokontrola

Łańcuchy module-scoped tylko w `serial`.


Przeglądarka w kontenerze Grid; równoległe testy UI/Selenium używają wielu sesji. Scenariusze ze wspólnym stanem (module-scoped) mają `@pytest.mark.serial` i uruchamiają się bez `-n`.

### Zmiany w kodzie

| Element | Rola |
|---------|------|
| `Settings.selenium_remote_url` | z `SELENIUM_REMOTE_URL`; same białe znaki → brak → lokalny Chrome |
| `SeleniumClient.start()` | `Chrome()` lub `Remote()`; przy błędzie startu — `quit()` i ponowne rzucenie wyjątku |
| `@pytest.mark.serial` | łańcuchy z `ui_client_module` / `selenium_client_module` w `test_login_page.py`, `test_secure_page.py`, `test_login_page_selenium.py`, `test_secure_page_selenium.py`; uruchamiać bez `-n` |
| `tests/test_selenium_client.py` | mocki Remote/Chrome + opcjonalnie żywy Grid |
| `docker-compose.yml` | Grid, `selenium-tests` / `selenium-tests-serial`, `playwright-tests` / `playwright-tests-serial` |
| `Dockerfile` target `playwright` | oficjalny obraz Playwright Python (przeglądarki w środku) |

Grid: `SE_NODE_MAX_SESSIONS=2` zgodne z `-n 2` w `selenium-tests`.

### Selektory w Compose

| Usługa | pytest `-m` |
|--------|-------------|
| `selenium-tests` | `selenium and not serial` |
| `selenium-tests-serial` | `selenium and serial` |
| `playwright-tests` | `ui and not selenium and not serial` |
| `playwright-tests-serial` | `ui and not selenium and serial` |

### Uruchomienie lokalne

```bash
docker compose --profile selenium up -d selenium
export SELENIUM_REMOTE_URL=http://localhost:4444
pytest -m "selenium and not serial" -n 2 -vv
pytest -m "selenium and serial" -vv
docker compose --profile selenium down

pytest -m "ui and not selenium and not serial" -n 2 -vv
pytest -m "ui and not selenium and serial" -vv
```

noVNC przy działającym `selenium`: [http://localhost:7900](http://localhost:7900).

### CI (`.github/workflows/ci.yml`)

1. `docker compose up … tests`  
2. `docker compose down`  
3. Selenium parallel → serial → `docker compose --profile selenium down`  
4. Playwright parallel → serial  

Brak kroku `playwright down` — na ephemeral runnerze zwykle wystarczy; opcjonalnie dodaj `docker compose --profile playwright down`.

### M1 ↔ M2

| Problem | M1 | M2 |
|---------|----|----|
| Wspólny MockServer | `xdist_group` + `loadgroup` | bez zmian |
| Jeden lokalny driver | loadgroup / sekwencyjnie | sesje Grid + `serial` dla module fixtures |
| Playwright w CI bez instalacji na runnerze | — | target `playwright` w Dockerze |

### Weryfikacja lokalna

- Mocki: `pytest tests/test_selenium_client.py -k "not connects_to_real" -q`
- Żywy Grid (serwis na `:4444`): `test_selenium_client_connects_to_real_grid` bez env ustawia `http://localhost:4444`; `test_selenium_client_connects_to_real_grid_2` wymaga `SELENIUM_REMOTE_URL` (fixtura `selenium_client`). W Compose/CI: `http://selenium:4444`.
- Playwright w Dockerze: pakiet `playwright` 1.63.x zgodny z obrazem `v1.63.0-noble`; równoległy UI — `-p no:anyio` (sync Playwright + xdist).
- Pary `*fixture_module` — tylko w przebiegu `serial`, nie pod `-n 2`.

Runner pytest i przeglądarka są rozdzielone: równoległość UI — wiele sesji Grid lub workerów Playwright, nie jeden współdzielony driver bez `@serial`.

## N1 — raporty Allure

<!-- readme-chapter:n1 -->
### O tym rozdziale

**N1** — Allure: metadane, kategorie, environment, kroki frameworka.

### Samokontrola

Behaviors, Categories, Environment w UI.


Allure przez `lab_fw.reporting`: etykiety (epic/feature/severity), steps/attachments, `categories.json`, dynamiczny `environment.properties` w `tests/conftest.py`. Workflow **CI** publikuje pełny przebieg Docker w `allure-results`; **tests** — węższy zestaw bez UI/compose.

### Co dodano

| Element | Rola |
|---------|------|
| `lab_fw.reporting` | `step`, `attach_*`, dekoratory `epic`, `feature`, `title`, `description`, `severity(SeverityLevel)`; bez allure — no-op |
| `tests/test_reporting.py` | marker `@pytest.mark.reporting` |
| `tests/test_api_client.py` | przykład `@feature("API Client")`, `@severity(SeverityLevel.CRITICAL)` |
| `categories.json` | **statyczny** plik w repo — reguły **Categories** w Allure |
| `tests/conftest.py` | przy `--alluredir`: kopiuje `categories.json`; zapisuje **dynamiczny** `environment.properties`; tylko master pytest, nie worker xdist |
| `docker-compose.yml` | `--alluredir=/app/allure-results`, volume `./allure-results` |
| `.github/workflows/ci.yml` | przygotowanie folderu, upload artefaktu; zakomentowane `# cp environment.properties` — **przykład** statycznego env (w projekcie env z conftest) |
| `Dockerfile` | `COPY categories.json` (conftest w kontenerze) |

### Pobieranie raportu z GitHub

| Workflow | Zawartość `allure-results` |
|----------|----------------------------|
| **tests** | unit/API bez UI/compose/selenium |
| **CI** | API + compose + parallel_lab + **Selenium + Playwright** (jeden katalog na runnerze) |

Pobierz ZIP → lokalnie `allure serve allure-results` ([Allure CLI](https://allurereport.org/docs/install/)).

### Uruchomienie lokalne

```bash
pytest -m reporting -q --alluredir=allure-results
pytest tests/test_api_client.py -q --alluredir=allure-results
allure serve allure-results
```

Przy `--alluredir` conftest umieszcza `categories.json` i `environment.properties` w `allure-results/`.

### Co sprawdzić w UI Allure

- **Behaviors** — epic/feature (oznaczone testy).
- **Categories** — reguły z `categories.json`.
- **Environment** — `environment.properties`.
- **Steps / Attachments** — `ApiClient` i `lab_fw.reporting.step`.

### TestRail i Jira

Etykiety feature/epic uzupełniają linki testcase/issue — zob. [N2](#n2--jira--testrail).

## N2 — Jira i TestRail

<!-- readme-chapter:n2 -->
### O tym rozdziale

**N2** — traceability: pytest, TestRail, Jira, Allure; dwa kanały.

### Samokontrola

Links w Allure; `test_id` = `C1`; filtr Assigned To.


Powiązanie przebiegu pytest z case’ami TestRail i zadaniami Jira: linki w Allure (`@testcase`, `@issue`), pole References w TestRail, opcjonalny upload przez trcli. Grupowanie po `feature` i `severity` — [N1](#n1--raporty-allure).

### Po co cztery systemy

| System | Rola |
|--------|------|
| **pytest** | Uruchamia kod; pass/fail to wynik wykonania. |
| **Allure** | Raport: kroki, załączniki, **Links** do narzędzi zewnętrznych. |
| **TestRail** | **Case’y**, suite, milestone, **test run**. |
| **Jira** | **Praca zespołu** (story, task, bug) i historia dyskusji. |

Autotest w Git to nie wszystko: TestRail — „co weryfikujemy”, Jira — „po co”, Allure — „co wyszło w ostatnim przebiegu”.

### Dwa osobne kanały powiązania

Często się je myli — to **różne** mechanizmy:

```text
  (A) Linki Allure       pytest --alluredir  →  @testcase / @issue  →  Links w raporcie
  (B) Test run TR        pytest --junitxml   →  trcli parse_junit   →  Run + statusy w TR
```

- **(A)** nie zapisuje wyników w TestRail; tylko linki TMS / Issue w Allure.
- **(B)** nie dodaje linków w Allure; wysyła pass/fail do **Test Run** (np. „N2 pytest API client results”).
- **References** w case TestRail — ręczny link zwrotny „ten case = ten node id pytest”.

Można używać obu; wystarczy jeden, jeśli znasz ograniczenia.

### Kod: dekoratory `lab_fw.reporting`

W N1 były `@feature` / `@severity`. W N2 doszły:

| Dekorator | Allure | Typowy URL |
|-----------|--------|------------|
| `@testcase(url, name=…)` | Link → TestRail | `https://<instance>.testrail.io/index.php?/cases/view/<id>` |
| `@issue(url, name=…)` | Link → Jira | `https://<site>.atlassian.net/browse/<KEY>-<n>` |

Bez `allure-pytest` dekoratory to **no-op**. Przykład z `tests/test_api_client.py`:

```python
from lab_fw.reporting import feature, severity, SeverityLevel, testcase, issue

@issue("https://andrzejszamborski08.atlassian.net/browse/KAN-4")
@testcase("https://andrzejszamborski.testrail.io/index.php?/cases/view/1", name="C1")
@feature("API Client")
def test_get_ok_with_mock_transport(record_property):
    record_property("test_id", "C1")
    ...
```

W `@issue` lepiej **`/browse/KAN-4`** niż URL tablicy z parametrami query.

Testy dekoratorów: `pytest -m reporting -q` (`tests/test_reporting.py`).

### Przykładowa mapa (HP QA Junior Prep)

| Case TestRail | pytest node id | Dekoratory Allure |
|---------------|----------------|-------------------|
| **C1** — GET /users returns 200 | `tests.test_api_client#test_get_ok_with_mock_transport` | `@testcase(…/view/1)`, `@feature("API Client")` |
| **C2** — Connection error → ApiError | `tests.test_api_client#test_request_http_error_becomes_api_error` | `@testcase(…/view/2)`, `@severity(CRITICAL)` |
| Jira **KAN-4** (powiązanie pytest ↔ TestRail) | oba testy | `@issue(…/browse/KAN-4)` |

### TestRail: pola case’a

W suite (sekcja **API Client**):

- **Type:** Automated · **Is Automated:** Yes  
- **References:** node id pytest i opcjonalnie Jira, np.  
  `tests.test_api_client#test_get_ok_with_mock_transport, Jira KAN-4`  
- **Steps / Expected:** scenariusz mock API (jak w C1/C2)

Id w URL (`view/1`) to **globalne id case’a**, nie numer wiersza w drzewie suite.

### Allure: podgląd linków

```bash
pytest tests/test_api_client.py -q --alluredir=allure-results
allure serve allure-results
```

- **Behaviors → API Client** — grupowanie `@feature`.  
- Karta testu → **Links** — TestRail i Jira.

Warstwa reporting: [Reporting / Allure](src/lab_fw/reporting/README.pl.md).

### TestRail CLI (kanał B)

1. JUnit (`test_id` musi być **`C1`**, **`C2`** — z prefiksem **C** jak w UI TestRail):

```bash
pytest tests/test_api_client.py --junitxml=testrail-results.xml
```

2. Sekrety w `.env` w repo (gitignore):  
   `TESTRAIL_URL`, `TESTRAIL_EMAIL`, `TESTRAIL_API_KEY`.

3. [TestRail CLI](https://github.com/gurock/trcli), potem:

```bash
bash scripts/upload_testrail.sh
```

Skrypt: `trcli parse_junit`, `--case-matcher property`, `--suite-id 1` (dostosuj do projektu).

### TestRail UI: typowe problemy

| Objaw | Częsta przyczyna |
|-------|------------------|
| Podsumowanie **2 Passed**, lista **No tests found** | Filtr **Assigned To** — usuń go lub wybierz **All**. |
| trcli nie dopasowuje case’ów | W JUnit `test_id` to `C1`, nie `1`. |
| Jira „Select organization” nic nie robi | Blokada popup; obejście: [GitHub App Jira](https://github.com/apps/jira/installations/new) i repo `hp-qa-junior-prep`. |

### Jira + GitHub (osobno od pytest)

**GitHub for Atlassian** łączy **commity i PR** z kluczem issue (`KAN-4` w message/title/branch) — panel **Development**. To **nie** zastępuje `@issue` w Allure.

### Pliki w repozytorium (N2)

| Ścieżka | Znaczenie |
|---------|-----------|
| `src/lab_fw/reporting/allure_tools.py` | `testcase`, `issue`, `decor_allure` |
| `tests/test_api_client.py` | przykład API Client z linkami |
| `tests/test_reporting.py` | testy dekoratorów |
| `scripts/upload_testrail.sh` | wrapper trcli |
| `pyproject.toml` | `python_functions = ["test_*"]` — pytest nie zbiera importu `testcase` jako testu |

`testrail-results.xml` i lokalne allure — w `.gitignore`.

## Allure (skrót)

<!-- readme-chapter:allure_short -->
### O tym rozdziale

Skrót poleceń Allure. Pełny rozdział: [N1](#n1--raporty-allure).


```bash
pytest -q --alluredir=allure-results
allure serve allure-results
```

Szczegóły: [N1](#n1--raporty-allure), [N2](#n2--jira--testrail) i [Reporting](src/lab_fw/reporting/README.pl.md).

Upload artefaktu: `if: always()` (workflow **tests** i **CI**).

## Dokumentacja modułów

<!-- readme-chapter:modules -->
### O tym rozdziale

Szczegóły modułów: API → mocks → reporting → UI → plugin → README_PYTEST.


- [API](src/lab_fw/api/README.pl.md)
- [UI](src/lab_fw/ui/README.pl.md)
- [Reporting / Allure](src/lab_fw/reporting/README.pl.md)
- [Pytest plugin](src/lab_fw/pytest_plugin/README.pl.md)
- [Pytest notes](tests/README_PYTEST.pl.md)
- [Mocks lab](tests/mocks_lab/README.pl.md)

## Dodatkowo

<!-- readme-chapter:extra -->
### O tym rozdziale

Zewnętrzny plan rozwoju — [PLAN_MID_HP.md](PLAN_MID_HP.md).


Plan rozwoju umiejętności: [PLAN_MID_HP.md](PLAN_MID_HP.md).
