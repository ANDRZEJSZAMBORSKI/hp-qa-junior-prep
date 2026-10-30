### О разделе

Карта репозитория: где лежит переиспользуемый код фреймворка, где сценарии pytest, как связаны Docker и CI.

### Дерево (основное)

| Путь | Содержимое |
|------|------------|
| `src/lab_fw/api/` | `ApiClient`, retry, auth, ошибки |
| `src/lab_fw/ui/` | Playwright / Selenium clients, page objects |
| `src/lab_fw/config/` | `Settings`, env, pydantic |
| `src/lab_fw/reporting/` | Allure decorators, steps, attachments |
| `src/lab_fw/pytest_plugin/` | hooks, markers integration |
| `src/distributed_lab/` | `Job`, `Worker`, `InMemoryQueue` (L2) |
| `src/device_lab/` | Mock cloud inventory, DFU handler (J3) |
| `tests/` | все pytest-модули |
| `tests/device_lab/` | HTTP-контракт inventory, маркер `device_lab` |
| `tests/mocks_lab/` | чистые моки и MockTransport (I2) |
| `tests/distributed_lab/` | L2/L3 |
| `tests/parallel_lab/` | M1, xdist и файлы |
| `scripts/` | вспомогательные скрипты (TestRail upload) |
| `categories.json` | правила Allure Categories |
| `.github/workflows/` | **tests** и **CI** |

### Два слоя

- **`lab_fw`** — библиотека, которую импортируют тесты; её можно ставить editable и переиспользовать в других проектах.
- **`tests/`** — демонстрация паттернов; падение теста часто указывает на регрессию фреймворка или контракта.

### Самопроверка

Открой `pyproject.toml`: `[tool.setuptools.packages.find] where = ["src"]`. Убедись, что после install `import lab_fw` работает из корня репо.
