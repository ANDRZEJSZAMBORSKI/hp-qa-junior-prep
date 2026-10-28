# Device lab — mock cloud inventory

[RU](README.md) · **EN** · [PL](README.pl.md)

Teaching test suite and **cloud inventory** contract for IoT-style scenarios: device registration, heartbeat, states, and DFU **without** real Bluetooth or Docker. Implementation: `device_lab` under `src/device_lab/`.

Root overview: [J3 in README](../../README.en.md#j3--mock-device-inventory-api-cloud-and-dfu). Risk-based suites: [N3](../../README.en.md#n3--risk-based-testing-smoke-and-full-regression).

---

## Architecture

```text
  pytest tests/device_lab
        │
        ▼
  InMemoryInventory  ◄───  create_handler(inventory)
        │                        │
        │                        ▼
        │                  httpx.MockTransport
        │                        │
        └────────────────────────┼──► ApiClient (lab_fw)
                                 │
                           JSON /devices/…
```

| Module | Responsibility |
|--------|----------------|
| `models.py` | `DeviceState`, pydantic `Device`, `parse_device` |
| `inventory.py` | State transitions and DFU logic |
| `api.py` | HTTP routing and status codes |

Domain errors extend `DeviceLabError` in `lab_fw.core.errors`.

---

## States and fields

| Field | Type | Description |
|-------|------|-------------|
| `device_id` | `str` | Unique id |
| `firmware_version` | `str` | Current firmware |
| `state` | `DeviceState` | `online`, `offline`, `dfu_in_progress` |
| `last_seen_at` | `datetime \| None` | UTC last heartbeat |

### Transition table

| Current | Action | Next | Side effects |
|---------|--------|------|--------------|
| — | `register` | `offline` | `last_seen_at = None` |
| `offline` | `heartbeat` | `online` | `last_seen_at = now` |
| `offline` | `set_state(online)` | `online` | `last_seen_at` unchanged |
| `online` | `set_state(offline)` | `offline` | — |
| `online` | `start_dfu` | `dfu_in_progress` | FW unchanged |
| `dfu_in_progress` | `complete_dfu(v)` | `online` | FW = `v`, `last_seen_at = now` |
| `dfu_in_progress` | `fail_dfu` | `online` | FW unchanged |
| `dfu_in_progress` | `heartbeat` | `dfu_in_progress` | update `last_seen_at` only |

`set_state` does **not** enter or leave DFU.

### Exceptions

| Exception | When |
|-----------|------|
| `DeviceNotFoundError` | Unknown id |
| `InvalidStateTransitionError` | Illegal transition |
| `DfuAlreadyInProgressError` | Second `start_dfu` |
| `SchemaError` | Invalid `parse_device` input |

---

## HTTP API

Test base URL: `https://device-cloud.test`. Handler: `create_handler(inventory)`.

| HTTP | Path | Body | Effect |
|------|------|------|--------|
| GET | `/devices` | — | List all |
| GET | `/devices/{id}` | — | One device |
| POST | `/devices/{id}/heartbeat` | — | Heartbeat |
| POST | `/devices/{id}/dfu/start` | `{"target_version":"2.0.0"}` | Start DFU |
| POST | `/devices/{id}/dfu/complete` | `{"version":"2.0.0"}` | Complete |
| POST | `/devices/{id}/dfu/fail` | — | Fail DFU |
| POST | `/devices/{id}/dfu/set_state` | `{"state":"online"}` | Admin set_state |

`target_version` is validated but **not stored** on the device in this teaching model.

### Error JSON

| HTTP | error |
|------|-------|
| 404 | `device_not_found`, `not_found` |
| 409 | `invalid_state_transition` |
| 400 | `invalid_json`, `missing_*`, `invalid_*` |
| 405 | `method_not_allowed` |

---

## Test layout

| File | Focus |
|------|--------|
| `test_models.py` | `parse_device`, strict pydantic |
| `test_inventory_states.py` | Inventory + DFU + ghost online |
| `test_inventory_api.py` | HTTP + `ApiClient` |

Marker: **`@pytest.mark.device_lab`**.

---

## Commands

```bash
pytest tests/device_lab -m device_lab -q
pytest --collect-only -q -m device_lab
pytest tests/device_lab/test_inventory_states.py -v
```

No compose, Playwright, or Selenium required. Included in CI filter `not ui and not selenium and not compose`.

---

## Cross-links

| Section | Link |
|---------|------|
| **N3** | `-m device_lab` as cloud/inventory slice |
| **mocks_lab** | MockTransport handler pattern |
| **api** | `ApiClient`, `Settings` |
| **distributed_lab** | DFU duration ≈ async work; L1 idempotency for POST |

---

## Extension pitfalls

1. Shared in-memory `Device` instances mutate across calls.
2. FW version changes only on `complete_dfu`, not `start_dfu`.
3. Do not exit DFU via `set_state` — use `complete_dfu` / `fail_dfu`.
4. `online` without heartbeat → `last_seen_at is None` (ghost online).
