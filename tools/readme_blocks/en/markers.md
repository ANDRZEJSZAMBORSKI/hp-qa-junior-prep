### About this section

Markers select test subsets and drive CI. They **do not** start infrastructure.

### CI usage

| Workflow | Filter | Effect |
|----------|--------|--------|
| **tests** | `not ui`, `not selenium`, `not compose` | fast runner, no Docker |
| **CI** / Docker CMD | often includes compose | needs `mock-api` |
| Compose services | see M2 | `serial` vs parallel UI |

### Learning tracks

- `distributed_lab` — L2/L3.
- `parallel_lab` — M1.
- `device_lab` — J3, in-process mock cloud (in **tests** CI filter).
- `reporting` — Allure decorators.

### Self-check

Run `pytest --markers` and confirm `compose`, `serial`, `distributed_lab` descriptions.
