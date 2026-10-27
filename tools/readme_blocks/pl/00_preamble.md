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
| **N1–N3** | Allure, TestRail, Jira, zestawy risk-based | `src/lab_fw/reporting/`, `tests/test_api_client.py`, `pyproject.toml` (markery) |

Proponowana kolejność: **Szybki start → Struktura → I1–I4 → L1 → L2 → L3 → M1 → M2 → N1 → N2 → N3**. Sekcje **Docker** i **GitHub Actions** warto mieć pod ręką przy każdym uruchomieniu.

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
15. [N3 — risk-based (smoke / full)](#n3--testy-oparte-na-ryzyku-smoke-i-pełna-regresja)
16. [Allure (skrót)](#allure-skrót)
17. [Dokumentacja modułów](#dokumentacja-modułów)

### Jak czytać rozdziały

Na początku sekcji jest **O tym rozdziale**: cel, pliki w repo, samokontrola. Potem tabele i polecenia. Przy padnięciu testu — najpierw [I4](#diagnostyka-padających-testów-i4), przy problemach infrastruktury — [L3](#l3--badanie-awarii-checklista).
