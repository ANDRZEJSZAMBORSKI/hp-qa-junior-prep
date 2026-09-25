# Mocks lab

[RU](README.md) · **EN** · [PL](README.pl.md)

Training module: **pure mocks** (`unittest.mock`, `patch`, spy, `monkeypatch`) and **`httpx.MockTransport`** on our `ApiClient` / `Settings` / `ApiError` / `retry_call` / logging / pytest.

Goal — not “green pytest for the badge”, but being able to explain in an interview: *what we replace, at which seam, and why*.

---

## How to run

From the `hp-qa-junior-prep` repo root (venv active):

```bash
# whole lab
pytest -v tests/mocks_lab

# pure mocks only
pytest -v -m mocks_pure tests/mocks_lab

# MockTransport only
pytest -v -m mocks_httpx tests/mocks_lab

# everything marked mocks
pytest -v -m mocks tests/mocks_lab

# smoke cases from the lab (stub / spy / monkeypatch)
pytest -v -m smoke tests/mocks_lab
```

Expect: `INFO [lab_fw.api] …` logs; on retry — `WARNING [lab_fw.core.retry] …`; all tests **passed** at the end.  
Full repo run: `pytest -q` (lab + the rest of `lab_fw` tests).

---

## Layout

| File | Contents |
|------|----------|
| `test_unittest_mock_basics.py` | `Mock`: `return_value`, `side_effect`, `call_count`, `call_args_list` |
| `test_mock_patch_api_client.py` | `patch.object` / `patch(httpx.Client)` / `MagicMock` / `ConnectError` → `ApiError` |
| `test_mock_side_effect_and_calls.py` | `side_effect` + custom `@retry` and `retry_call` |
| `test_mock_vs_spy.py` | stub vs `Mock(wraps=…)` vs `monkeypatch.setattr` |
| `test_mock_transport_basics.py` | `MockTransport`: `Settings` built **manually** in the test |
| `test_mock_transport_basics_02.py` | same ideas, but `settings` from a **fixture** (`conftest`) |

Two transport files and some overlapping cases are **intentional**: compare styles (manual `Settings` vs fixture; one fat test vs `@parametrize`).

Markers (`mocks`, `mocks_pure`, `mocks_httpx`, `smoke`) are placed where they help filtering — not as a single product-wide policy.

---

## Part I — pure mocks

We replace a **Python object or method**:

- `Mock` / `MagicMock` — no real HTTP;
- `patch` / `patch.object` — temporarily replace `request` or `httpx.Client`;
- `wraps=` — spy: real function + call history;
- `monkeypatch` — pytest way to replace a class/module attribute for the test.

Pros: fast, precise, good for unit tests.  
Cons: easy to patch the wrong seam; weak visibility of a real `httpx.Request` (path/params/headers/body).

---

## Part II — `httpx.MockTransport`

We replace the **transport** of a real `httpx.Client` inside `ApiClient`:

```text
ApiClient → httpx.Client(transport=MockTransport(handler)) → handler(request) → Response | raise
```

The handler sees a real `httpx.Request` (method, path, params, headers) and can:

- return JSON / text / a chosen status;
- raise `ConnectError` / `ReadTimeout` → our client raises `ApiError` (`__cause__` kept);
- keep state (retry: 2 failures → success).

Pros: closer to a real HTTP stack without the network; DI via `transport=` is cleaner than endless `patch`.  
Cons: a bit more handler code; still not a live API.

---

## When to use what (cheat sheet)

| Task | Usually |
|------|---------|
| Test your retry / a branch without HTTP | `Mock` + `side_effect` |
| Replace one method on an already built client | `patch.object` |
| Avoid creating a real `httpx.Client` | `patch("…httpx.Client")` |
| Assert the right path/params/header went out | `MockTransport` + assert on `request` |
| Network error / timeout through the client | `MockTransport` raise **or** `patch` + `side_effect` |
| `ApiClient` + `retry_call` integration | `MockTransport` with an attempts counter |

For HP mid: **MockTransport / DI transport** is the main style for an API client; pure mocks — for isolating helpers and narrow unit tests.

---

## Tie-in with `lab_fw`

- `ApiClient(settings, transport=…)` — extension point.
- `ApiError` wraps `httpx.HTTPError`.
- `retry_call` / training `@retry` — around client calls.
- Logging is already started in root `tests/conftest.py` (`pytest_configure` → `setup_logging`).
