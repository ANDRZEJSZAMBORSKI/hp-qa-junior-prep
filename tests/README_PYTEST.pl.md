# Pytest notes (lab_fw)

[RU](README_PYTEST.md) · [EN](README_PYTEST.en.md) · **PL**

Krótkie zasady izolacji i hygiene dla tego repo.

## Scope fixture’ów

| Scope | Kiedy |
|-------|--------|
| `function` (domyślnie) | prawie zawsze: client, transport, dane tymczasowe |
| `module` | drogi, niezmienny setup na plik |
| `session` | rzadko; łatwo zepsuć xdist shared state |

`api_client` w root `conftest`: `yield` → `close()` (jak context manager).

## Hierarchia conftest

- `tests/conftest.py` — wspólne (settings, logging, `api_client`)
- `tests/mocks_lab/conftest.py` — tylko dla poddrzewa `mocks_lab/` (np. `mock_handler`)

Lokalny conftest nie jest widoczny dla testów poza swoim folderem.

## xdist

```bash
pytest -q -n auto
```

Źle: globalny mutable na poziomie modułu, wspólny plik/port bez izolacji, zależność od kolejności.  
Dobrze: stan w fixture z `yield`, MockTransport zamiast sieci, każdy test ma własne otoczenie.

Demo: `tests/test_xdist_isolation.py` (zły przypadek ma `skip`).

## Anti-flaky checklist

1. Testy nie zależą od kolejności.
2. Brak shared mutable między testami.
3. Unit bez prawdziwej sieci — mock / MockTransport.
4. Nie używać `sleep` jako warunku sukcesu.
5. Przy `-n auto` suite ma być zielony tak samo jak bez niego.

## Przydatne komendy

```bash
pytest -q
pytest -q -n auto
pytest -q tests/test_fixtures_scopes.py
pytest -q tests/test_xdist_isolation.py
```
