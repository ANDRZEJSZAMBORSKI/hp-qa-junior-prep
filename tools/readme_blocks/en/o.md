### About this chapter

**O** covers automation **reliability**: controlled **HTTP retry**, **anti-flaky** hygiene, **quality gates** in GitHub Actions, and **AI-assisted** development with mandatory verification. It builds on `lab_fw`, `.github/workflows/`, and [tests/README_PYTEST.md](tests/README_PYTEST.md).

Related chapters: [L1](#distributed-systems-theory-and-terms-l1), [L2](#l2--queue-retry-timeout-deadline-idempotency), [L3](#l3--failure-investigation-checklist), [N3](#n3--risk-based-testing-smoke-and-full-regression), [M1](#m1--parallel-execution-and-resource-isolation), [J3](#j3--mock-device-inventory-api-cloud-and-dfu) (POST DFU without blind retry).

---

### O1 — Retry policy (HTTP client)

**Source of truth:** `src/lab_fw/api/retry_policy.py` → `should_retry(exc)`; orchestration — `src/lab_fw/core/retry.py` → `retry_call`.

| Situation | Retry? |
|-----------|--------|
| **GET** + HTTP **429**, **503** | Yes |
| **GET** + HTTP 400, 401, 404, 422, **500**, … | No |
| **GET** + transport (ConnectError, ReadTimeout, …) | Yes |
| **POST** + any status or transport | **No** |

**Why no POST retry:** the server may have already applied the operation; a repeat causes **duplicate side effects** (record, payment, second `start_dfu`). After a POST timeout you need **idempotency** and an explicit policy (see L2), not a blind loop.

**GET + 500 no retry:** that is an **application error** response; repeats hide defects and load the system. Retry only **transient** cases (503, 429, network).

**429:** policy allows retry on GET; in production you respect **`Retry-After`**; in the lab client, pause comes from **backoff + jitter** in `retry_call`, without parsing the header.

**`retry_call` parameters:**

- `attempts=3` — three calls to `fn()` total (first try + two retries).
- `retry_if=True` — before each retry **`should_retry`** runs; with `retry_if=False` you can get “blind” retry via `retry_on` (unsafe for POST).
- When attempts are exhausted, the **last** exception is raised — success is not faked.

```bash
pytest tests/test_api_retry_policy.py -m api -q
pytest tests/test_api_retry_policy.py -v -k "503" --log-cli-level=WARNING
```

**Client retry ≠ pytest-rerun:** `pytest-rerunfailures` on the whole suite can hide flaky tests or real bugs; treat flaky via **O2**, not global reruns.

---

### O2 — Anti-flaky and quarantine

Checklist: [tests/README_PYTEST.md](tests/README_PYTEST.md) → **Anti-flaky checklist**.

1. Tests **must not depend on execution order**.
2. **No shared mutable state** between tests (module-level lists/dicts, one file without isolation).
3. Unit/API **without real network** — MockTransport / mock handler.
4. **No `sleep`** as success criteria — wait for **state** with a timeout (UI element, job status, JSON body).
5. Suite is **green** both without `-n auto` and with **`pytest -q -n auto`**.

**xdist:** each worker is a separate process; prefer a **unique** file/record/fixture per test; if a shared resource is unavoidable — **FileLock** (`tests/parallel_lab/`, M1) or **`@pytest.mark.xdist_group`**. Marker **`serial`** — tests that must not run in parallel with others; the actual mode is the **pytest command** (do not mix `serial` UI with `-n auto` without a group).

**Quarantine (process):** reproduce → logs / Allure → root cause → fix; if fix is not immediate — **`@pytest.mark.skip(reason=…)`** + issue, **not** `--reruns 10` on all of CI.

```bash
pytest -q -n auto
pytest tests/parallel_lab -m parallel_lab -n 2 -q
```

---

### O3 — Quality gates in CI

Two gate levels (see [GitHub Actions](#github-actions)):

| Workflow | Runner | What it checks |
|----------|--------|----------------|
| **`tests.yml`** | `ubuntu-latest`, pip | `pytest -m "not ui and not selenium and not compose" -q -n auto`, secret `LAB_FW_API_TOKEN`, Allure artifact |
| **`ci.yml`** | Docker Compose | `mock-api`, compose tests, Selenium and Playwright (parallel + **serial**), cleanup `if: always()` |

**Shift-left:** **Check secret** fails **before** pytest if the token is empty.

**CI-filter (tests.yml):** includes API, mocks, `distributed_lab`, `parallel_lab`, **`device_lab`**, reporting — **excludes** `ui`, `selenium`, `compose` (browser / MockServer in container).

**Smoke (`-m smoke`, ~17 tests)** — fast local signal; **does not** replace CI-filter (~**391** tests). **Full collection** — ~**476** (recount: `pytest --collect-only -q`).

**`if: always()`** on Allure upload — artifact for investigation on a **red** job; job status stays failed.

Local PR gate simulation:

```bash
pytest -m "not ui and not selenium and not compose" -q -n auto --tb=line
```

---

### O4 — AI-assisted development

Recommended cycle:

1. **Requirements and constraints** (API contract, “do not change tests without agreement”).
2. **Agent** (e.g. Cursor): scaffold, docs, repo search, drafts.
3. **Review diff** — domain, security, style, fit with `lab_fw`.
4. **pytest** locally; for large changes — **CI-filter**; if needed — full **`ci.yml`** locally via Compose.
5. **Merge** only after review and green gate; flaky — **O2**, not weakening CI.

AI speeds up drafts; **quality** comes from tests, logs, and your review — same as any PR.

---

### Summary table

| Topic | Key files / commands |
|-------|----------------------|
| Retry | `retry_policy.py`, `test_api_retry_policy.py` |
| Flaky | `tests/README_PYTEST.md`, `test_xdist_isolation.py`, `parallel_lab` |
| Gates | `.github/workflows/tests.yml`, `ci.yml`, N3 |
| AI | Review + pytest + Actions |

### Self-check

1. Name three cases where **GET** retries and one where **POST** does not.
2. How does **smoke** differ from the **tests.yml** filter?
3. Why is **`distributed_lab`** in CI-filter but **`compose`** is not?
4. Why does **`upload-artifact: if: always()`** not make the job green?
5. In one paragraph: your AI workflow from spec to merge.
