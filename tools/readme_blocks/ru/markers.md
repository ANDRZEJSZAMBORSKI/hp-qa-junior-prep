### О разделе

Маркеры — «рубильники» для выбора подмножества тестов и для CI. Они **не** поднимают инфраструктуру сами.

### Как CI использует маркеры

| Workflow | Фильтр | Эффект |
|----------|--------|--------|
| **tests** | `not ui`, `not selenium`, `not compose` | быстрый runner без Docker |
| **CI** / Docker CMD | часто без `not compose` | compose-тесты при живом `mock-api` |
| Compose services | см. M2 | `serial` vs параллельный UI |

### Учебный смысл

- `distributed_lab` — L2/L3, без Docker.
- `parallel_lab` — M1, xdist и файлы.
- `device_lab` — J3, mock cloud inventory in-process (входит в CI-filter **tests**).
- `reporting` — декораторы Allure.

### Самопроверка

`pytest --markers | findstr /i compose` (Windows) или `pytest --markers | rg compose` — описание из `pyproject.toml`.
