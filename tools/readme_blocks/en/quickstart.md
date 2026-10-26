### About this section

The shortest path from a clean machine to a green unit/API run without a browser or MockServer — the same slice as the GitHub **tests** workflow (no `compose` marker).

### Step by step

1. Clone the repo and `cd` into the root.
2. Create a **Python 3.11+** venv and activate it.
3. `pip install -e ".[dev]"` — editable `lab-fw` plus pytest, xdist, allure, playwright, selenium, filelock.
4. Run the fast suite (command below). Expect hundreds of passes; runtime is a few minutes on a laptop.

### Marker filter

`-m "not ui and not selenium and not compose"` skips tests that need a real browser or the `mock-api` container. You do not need Docker or `playwright install` for the first green run.

### UI (separate step)

Playwright and Selenium need a browser. For Playwright run `playwright install chromium`. Selenium 4 on Windows often resolves Chrome via Selenium Manager.

### Self-check

| Question | Where to look |
|----------|----------------|
| Editable install? | `python -m pip show lab-fw` → Location under your `.venv` |
| xdist active? | pytest output shows `[gw0]` with `-n auto` |
| Why no compose tests? | No MockServer — see Docker |

### Common issues

- **Wrong Python** — recreate the venv with 3.11+.
- **Import errors** — venv activated? `pip install -e ".[dev]"` done?
- **Playwright** — do not run `-m ui` before `playwright install`.
