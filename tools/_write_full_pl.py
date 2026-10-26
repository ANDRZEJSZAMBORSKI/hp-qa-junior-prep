#!/usr/bin/env python3
"""Write complete Polish source blocks for L1 and module deep sections (UTF-8, no BOM)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent

L1: dict[int, str] = {
    1: """#### O punkcie 1 — komunikacja asynchroniczna

**Sens:** kod wywołujący nie blokuje się do końca przetwarzania; wynik obsługuje później inny komponent.

**W repozytorium:** kolejka `InMemoryQueue` + `Worker.run_once()` — wrzucasz `Job`, HTTP wykona się przy następnym `run_once`, a nie w momencie `put`.

```python
# src/distributed_lab/queue_worker.py (idea)
queue.put(job)
worker.run_once()  # jeden job → HTTP przez ApiClient
```

**QA:** testuj osobno „przyjęte do przetwarzania” i „stan końcowy”; nie traktuj tego jak fire-and-forget bez asercji.

**Sprawdzenie:** `pytest tests/distributed_lab/test_queue_worker.py -q`
""",
    2: """#### O punkcie 2 — kolejka / zdarzenie / broker

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
""",
    3: """#### O punkcie 3 — retry a timeout

**Retry** odpowiada na pytanie „czy powtórzyć po błędzie”; **timeout** — „jak długo czekać na jedną próbę”. Po timeoutie wynik po stronie serwera jest **nieznany** — ślepy retry POST jest niebezpieczny bez idempotency.

**Polityka w kodzie** (`src/lab_fw/api/retry_policy.py`):

```python
def should_retry(exc: ApiError) -> bool:
    # GET + 429/503 lub GET + błąd transportu → True
    # POST → False
```

**Orkiestracja:** `lab_fw.core.retry.retry_call` woła `should_retry` między próbami.

**Sprawdzenie:** `pytest tests/test_api_retry_policy.py tests/distributed_lab/test_l3_investigation.py -q`
""",
    4: """#### O punkcie 4 — timeout

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
""",
    5: """#### O punkcie 5 — idempotency

**Nagłówek na wire** (bez mutacji modelu joba):

```python
# src/distributed_lab/queue_worker.py
if job.idempotency_key is not None:
    kwargs["headers"]["Idempotency-Key"] = job.idempotency_key
```

**Serwer testowy** w `tests/distributed_lab/test_timeout.py`: powtórny POST z tym samym kluczem nie zwiększa `received_requests`.

**Polityka retry:** POST **nie** jest retryowany w `should_retry` / workerze — ochrona przed podwójnym efektem ubocznym.

**Sprawdzenie:** `pytest tests/distributed_lab/test_timeout.py -q -k idempotency`
""",
    6: """#### O punkcie 6 — eventual consistency

**Idea:** stany systemów mogą chwilowo się różnić; test czeka na zgodność z **deadline**, a nie na stały `sleep`.

**W repozytorium:** worker sprawdza pozostały czas przez `_remaining_time` przed i po HTTP; warstwa UI używa jawnych waitów (`PlaywrightWait` / `SeleniumWait`) zamiast ślepej pauzy.

**Wzorzec QA:**

```python
# antywzorzec: time.sleep(5)
# lepiej: wait z timeoutem ze settings (ui_timeout_s / deadline joba)
```

**Sprawdzenie:** `pytest tests/test_playwright_wait.py tests/test_selenium_wait.py -q`
""",
    7: """#### O punkcie 7 — logi, metryki, trace

| Sygnał | Przykład w repozytorium |
|--------|-------------------------|
| **Logi** | `INFO lab_fw.api`, `WARNING lab_fw.core.retry` przy retry |
| **Metryki** | ręczne liczniki L3: `http_requests`, `503_count` |
| **Trace** | brak pełnego OTel; jest wire ID `X-Request-ID` (pkt 8) |

**Praktyka L3:** `caplog` łapie dwa WARNING przed udanym retry 503→200.

**Sprawdzenie:** `pytest tests/distributed_lab/test_l3_investigation.py -q`
""",
    8: """#### O punkcie 8 — correlation / Request / Trace ID

**W repozytorium:** job przekazuje nagłówki bez zmian — testy ustawiają `X-Request-ID`:

```python
# tests/distributed_lab/test_timeout.py — nagłówki joba na HTTP
headers={"X-Request-ID": "req-123"}
```

**Retry:** każda próba GET może powtórzyć ten sam `Idempotency-Key`; polityka Request ID zależy od API (tu — to, co włożysz w job).

**QA:** przeszukaj repo: `grep -Rni "X-Request-ID" src tests`

**Sprawdzenie:** `pytest tests/distributed_lab/test_timeout.py -q -k request`
""",
    9: """#### O punkcie 9 — env a build

**Env (przykład L3):** lokalnie `LAB_FW_API_TOKEN` może być pusty; w workflow CI **tests** secret jest **wymagany**.

**Build:** `git rev-parse HEAD`, editable `lab-fw`, target obrazu Docker `ci` vs `local` (Avast CA).

```bash
python -c "import os; print(os.getenv('LAB_FW_API_TOKEN', 'MISSING'))"
docker compose config | head
```

**QA:** pada tylko w CI → najpierw porównaj env i polecenia pytest w `.github/workflows/`, nie „przepisuj test”.

**Sprawdzenie:** przeczytaj `tests/distributed_lab/test_l3_investigation.py` (sekcje env/build).
""",
}

MODULES: dict[str, dict[str, str]] = {
    "api": {
        "00_preamble": """### O module API

Pakiet `lab_fw.api` — klient HTTP z jawną polityką błędów, opcjonalnym Bearer, schematami pydantic i retry **opt-in**. Dokument powiązany z README głównym **I1–I3** oraz [mocks_lab](../../../tests/mocks_lab/README.pl.md).

**Pliki:** `client.py`, `auth.py`, `schemas.py`, `retry_policy.py`.""",
        "install": """#### O sekcji — instalacja

Instalacja editable dołącza `httpx`, `pydantic` (dev). Bez `[dev]` część testów jest niedostępna.""",
        "settings": """#### O sekcji — Settings

`get_settings()` czyta env raz na proces; zob. README główne „Zmienne środowiskowe”. Token jest opcjonalny — wiele testów używa MockTransport bez Bearer.""",
        "bearer": """#### O sekcji — Bearer

Nagłówek ustawiany przy tworzeniu klienta, gdy `api_token` jest podany. Odświeżenie tokenu po OAuth — `set_bearer_token`.""",
        "oauth": """#### O sekcji — client credentials

Demo OAuth bez IdP: `fetch_client_credentials_token` → POST `/oauth/token` przez ten sam `ApiClient` (mockowany transport).

**Sprawdzenie:** `pytest tests/test_api_auth.py -q`""",
        "schema": """#### O sekcji — Schema

`parse_user` / `parse_token` centralizują walidację JSON → `SchemaError` zamiast KeyError w każdym teście.

**Sprawdzenie:** `pytest tests/test_api_schemas.py -q`""",
        "negative": """#### O sekcji — Negative / errors

4xx/5xx **domyślnie nie** rzucają wyjątku — jawny kontrakt. Transport → `ApiError` z `__cause__`.

**Sprawdzenie:** `pytest tests/test_api_negative.py tests/test_compose_api.py -q`""",
        "retry": """#### O sekcji — Retry policy

Retry tylko przez `retry_call`, nie wewnątrz każdego `get`. Tabela poniżej to źródło prawdy dla L1 pkt 3 i workera L2.

**Sprawdzenie:** `pytest tests/test_api_retry_policy.py -q`""",
        "tests": """#### O sekcji — testy API

Uruchamiaj plikami przy lokalizacji regresji; `-m api` — cały zestaw z markerem.""",
    },
    "reporting": {
        "00_preamble": """### O module reporting

Fasada nad Allure: testy nie importują `allure` bezpośrednio — łatwiej no-op bez `allure-pytest` i jeden styl steps/attachments. Zob. README główne **N1–N2**.""",
        "install": """#### O sekcji — instalacja

`allure-pytest` w `[dev]`. Bez niego dekoratory i steps są no-op.""",
        "api": """#### O sekcji — API reporting

Dekoratory przez `decor_allure`: epic/feature/severity/testcase/issue. `ApiClient` już emituje steps przy HTTP.""",
        "n1": """#### O sekcji — metadane N1

`categories.json` + dynamiczne `environment.properties` w `tests/conftest.py` (tylko proces master).""",
        "n2": """#### O sekcji — N2

Linki w Allure ≠ upload do TestRail (trcli). Oba opisane w README głównym N2.""",
        "run": """#### O sekcji — uruchomienie

`--alluredir` jest wymagany dla plików; `allure serve` tylko lokalnie.""",
        "tests": """#### O sekcji — testy warstwy

`pytest -m reporting` — nie zbiera nazwy `testcase` jako testu (`python_functions = test_*` w pyproject).""",
    },
    "mocks_lab": {
        "00_preamble": """### O module mocks_lab

**Katalog wzorców** podmiany zależności: od `unittest.mock` do `httpx.MockTransport`. Powiązany z **I2** oraz [README API](../../../src/lab_fw/api/README.pl.md).""",
        "run": """#### O sekcji — uruchomienie

Filtry `mocks_pure` / `mocks_httpx` dzielą część I i II bez ręcznego wypisywania plików.""",
        "structure": """#### O sekcji — struktura

Dwa pliki transportowe celowo powtarzają te same idee — porównaj fixture vs ręczne Settings.""",
        "pure": """#### O sekcji — czyste mocki

Patch „w złym miejscu” to częsty błąd juniora. Pytaj: podmieniamy **klienta**, **metodę** czy **transport**?""",
        "transport": """#### O sekcji — MockTransport

Preferowany styl dla `ApiClient(settings, transport=...)`. Handler widzi prawdziwy `httpx.Request`.""",
        "cheatsheet": """#### O sekcji — ściąga

Używaj tabeli przy code review: transport dla kontraktu HTTP, mock dla wąskiej gałęzi logiki.""",
        "tiein": """#### O sekcji — powiązanie z lab_fw

Logi retry są już w conftest — szukaj WARNING przy `pytest -v tests/mocks_lab`.""",
    },
}


def main() -> None:
    l1_dir = ROOT / "l1_deep_blocks" / "pl"
    l1_dir.mkdir(parents=True, exist_ok=True)
    for n, text in L1.items():
        (l1_dir / f"{n:02d}.md").write_text(text.strip() + "\n", encoding="utf-8")
    print(f"Wrote {len(L1)} L1 PL blocks")

    mod_root = ROOT / "module_deep_blocks"
    for module, files in MODULES.items():
        pl_dir = mod_root / module / "pl"
        pl_dir.mkdir(parents=True, exist_ok=True)
        for key, text in files.items():
            (pl_dir / f"{key}.md").write_text(text.strip() + "\n", encoding="utf-8")
        print(f"Wrote {len(files)} PL blocks for {module}")


if __name__ == "__main__":
    main()
