### About this section

A map of the repo: reusable framework code, pytest scenarios, and how Docker/CI tie in.

### Tree (main paths)

| Path | Contents |
|------|----------|
| `src/lab_fw/api/` | `ApiClient`, retry, auth, errors |
| `src/lab_fw/ui/` | Playwright / Selenium clients, pages |
| `src/lab_fw/config/` | `Settings`, env, pydantic |
| `src/lab_fw/reporting/` | Allure decorators, steps, attachments |
| `src/lab_fw/pytest_plugin/` | hooks, markers |
| `src/distributed_lab/` | `Job`, `Worker`, `InMemoryQueue` (L2) |
| `tests/` | all pytest modules |
| `tests/mocks_lab/` | pure mocks and MockTransport (I2) |
| `tests/distributed_lab/` | L2/L3 |
| `tests/parallel_lab/` | M1, xdist and files |
| `scripts/` | helpers (TestRail upload) |
| `categories.json` | Allure Categories rules |
| `.github/workflows/` | **tests** and **CI** |

### Two layers

- **`lab_fw`** — library imported by tests; editable install for reuse.
- **`tests/`** — pattern catalog; failures often signal framework or contract regressions.

### Self-check

In `pyproject.toml`, packages live under `src/`. After install, `import lab_fw` must work from the repo root.
