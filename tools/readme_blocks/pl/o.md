### O rozdziale

**O** — niezawodność automation: kontrolowany **retry** HTTP, higiena **anti-flaky**, **quality gates** w GitHub Actions oraz rozwój **wspomagany AI** z obowiązkową weryfikacją. Materiał opiera się na `lab_fw`, `.github/workflows/` i [tests/README_PYTEST.md](tests/README_PYTEST.md).

Powiązane rozdziały: [L1](#systemy-rozproszone-teoria-i-terminologia-l1), [L2](#l2--kolejka-retry-timeout-deadline-idempotency), [L3](#l3--śledztwo-awarii-checklista), [N3](#n3--testowanie-oparte-na-ryzyku-smoke-i-pełna-regresja), [M1](#m1--wykonanie-równoległe-i-izolacja-zasobów), [J3](#j3--mock-device-inventory-api-chmura-i-dfu) (POST DFU bez ślepego retry).

---

### O1 — Polityka retry (klient HTTP)

**Źródło prawdy:** `src/lab_fw/api/retry_policy.py` → `should_retry(exc)`; orkiestracja — `src/lab_fw/core/retry.py` → `retry_call`.

| Sytuacja | Retry? |
|----------|--------|
| **GET** + HTTP **429**, **503** | Tak |
| **GET** + HTTP 400, 401, 404, 422, **500**, … | Nie |
| **GET** + transport (ConnectError, ReadTimeout, …) | Tak |
| **POST** + dowolny status lub transport | **Nie** |

**Dlaczego brak retry POST:** serwer mógł już wykonać operację; powtórzenie daje **duplikat skutku** (zapis, płatność, drugi `start_dfu`). Po timeout POST potrzebne są **idempotency** i jawna polityka (L2), nie ślepa pętla.

**GET + 500 bez retry:** to odpowiedź o **błędzie aplikacji**; powtórzenia maskują defekt i obciążają system. Retry tylko przy **transient** (503, 429, sieć).

**429:** polityka pozwala retry na GET; w produkcji uwzględnia się **`Retry-After`**; w kliencie lab pauza to **backoff + jitter** w `retry_call`, bez parsowania nagłówka.

**Parametry `retry_call`:**

- `attempts=3` — trzy wywołania `fn()` łącznie (pierwsza próba + dwa powtórzenia).
- `retry_if=True` — przed powtórzeniem **`should_retry`**; przy `retry_if=False` możliwy „ślepy” retry przez `retry_on` (niebezpieczne dla POST).
- Po wyczerpaniu prób — **ostatni** wyjątek; sukcesu się nie symuluje.

```bash
pytest tests/test_api_retry_policy.py -m api -q
pytest tests/test_api_retry_policy.py -v -k "503" --log-cli-level=WARNING
```

**Retry klienta ≠ pytest-rerun:** `pytest-rerunfailures` na całym suite może ukryć flaky lub prawdziwy bug; flaky leczy się przez **O2**, nie globalnym rerun.

---

### O2 — Anti-flaky i kwarantanna

Checklista: [tests/README_PYTEST.md](tests/README_PYTEST.md) → **Anti-flaky checklist**.

1. Testy **nie zależą od kolejności** wykonania.
2. **Brak współdzielonego mutable state** między testami.
3. Unit/API **bez prawdziwej sieci** — MockTransport / mock handler.
4. **Bez `sleep`** jako warunku sukcesu — oczekiwanie na **stan** z timeoutem.
5. Suite **zielony** bez `-n auto` i z **`pytest -q -n auto`**.

**xdist:** każdy worker to osobny proces; unikalny plik/rekord/fixture na test; wspólny zasób — **FileLock** (`tests/parallel_lab/`, M1) lub **`@pytest.mark.xdist_group`**. Marker **`serial`** — testy, których nie wolno równoleglić z innymi; tryb wynika z **komendy pytest**.

**Kwarantanna:** reprodukcja → logi / Allure → root cause → fix; brak szybkiego fixu — **`@pytest.mark.skip(reason=…)`** + issue, **nie** `--reruns 10` na całym CI.

```bash
pytest -q -n auto
pytest tests/parallel_lab -m parallel_lab -n 2 -q
```

---

### O3 — Quality gates w CI

Dwa poziomy gate (patrz [GitHub Actions](#github-actions)):

| Workflow | Runner | Co sprawdza |
|----------|--------|-------------|
| **`tests.yml`** | `ubuntu-latest`, pip | `pytest -m "not ui and not selenium and not compose" -q -n auto`, sekret `LAB_FW_API_TOKEN`, artefakt Allure |
| **`ci.yml`** | Docker Compose | `mock-api`, testy compose, Selenium i Playwright (parallel + **serial**), cleanup `if: always()` |

**Shift-left:** krok **Check secret** pada **przed** pytest przy pustym tokenie.

**Filtr CI (tests.yml):** API, mocks, `distributed_lab`, `parallel_lab`, **`device_lab`**, reporting — **bez** `ui`, `selenium`, `compose`.

**Smoke (`-m smoke`, ~17 testów)** — szybki sygnał lokalny; **nie** zastępuje filtra CI (~**391** testów). **Pełna kolekcja** — ~**476** (`pytest --collect-only -q`).

**`if: always()`** przy upload Allure — artefakt przy **czerwonym** jobie; status joba pozostaje failed.

Lokalna symulacja gate PR:

```bash
pytest -m "not ui and not selenium and not compose" -q -n auto --tb=line
```

---

### O4 — Rozwój wspomagany AI

Zalecany cykl:

1. **Wymagania i ograniczenia** (kontrakt API, brak zmian testów bez uzgodnienia).
2. **Agent** (np. Cursor): scaffold, docs, wyszukiwanie, szkice.
3. **Review diff** — domena, security, styl, zgodność z `lab_fw`.
4. **pytest** lokalnie; duże zmiany — **filtr CI**; w razie potrzeby pełny **`ci.yml`** przez Compose.
5. **Merge** po review i zielonym gate; flaky — **O2**, nie osłabianie CI.

AI przyspiesza szkice; **jakość** dają testy, logi i Twój review — jak przy każdym PR.

---

### Tabela podsumowująca

| Temat | Pliki / komendy |
|-------|-----------------|
| Retry | `retry_policy.py`, `test_api_retry_policy.py` |
| Flaky | `tests/README_PYTEST.md`, `test_xdist_isolation.py`, `parallel_lab` |
| Gates | `.github/workflows/tests.yml`, `ci.yml`, N3 |
| AI | Review + pytest + Actions |

### Samokontrola

1. Trzy przypadki retry **GET** i jeden, gdy **POST** nie retry.
2. Czym **smoke** różni się od filtra **tests.yml**?
3. Dlaczego **`distributed_lab`** jest w filtrze CI, a **`compose`** nie?
4. Dlaczego **`upload-artifact: if: always()`** nie robi joba zielonym?
5. Jednym akapitem: Twój workflow AI od spec do merge.
