# Pytest notes (lab_fw)

[RU](README_PYTEST.md) · **EN** · [PL](README_PYTEST.pl.md)

Short isolation and hygiene rules for this repo.

## Fixture scopes

| Scope | When |
|-------|------|
| `function` (default) | almost always: client, transport, temp data |
| `module` | expensive immutable setup per file |
| `session` | rare; easy to break under xdist with shared state |

Root `api_client` fixture: `yield` → `close()` (same idea as a context manager).

## conftest hierarchy

- `tests/conftest.py` — shared (settings, logging, `api_client`)
- `tests/mocks_lab/conftest.py` — only for the `mocks_lab/` subtree (e.g. `mock_handler`)

A local conftest is not visible to tests outside its folder.

## xdist

```bash
pytest -q -n auto
```

Bad: module-level mutable globals, shared file/port without isolation, order-dependent tests.  
Good: state in a `yield` fixture, MockTransport instead of the network, each test owns its environment.

Demo: `tests/test_xdist_isolation.py` (bad case is `skip`ped).

## Anti-flaky checklist

1. Tests must not depend on order.
2. No shared mutable state across tests.
3. Units without real network — mock / MockTransport.
4. Do not use `sleep` as a success condition.
5. Under `-n auto` the suite must stay as green as without it.

## Useful commands

```bash
pytest -q
pytest -q -n auto
pytest -q tests/test_fixtures_scopes.py
pytest -q tests/test_xdist_isolation.py
```
