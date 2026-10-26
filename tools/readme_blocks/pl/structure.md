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
