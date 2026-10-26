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
