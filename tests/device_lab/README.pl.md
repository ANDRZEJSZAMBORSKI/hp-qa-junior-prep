# Device lab — mock inventory w chmurze

[RU](README.md) · [EN](README.en.md) · **PL**

Zbiór testów edukacyjnych i kontrakt **chmurnego inventory** dla scenariuszy IoT: rejestracja urządzenia, heartbeat, stany i DFU **bez** Bluetooth i **bez** Dockera. Implementacja: `device_lab` w `src/device_lab/`.

Przegląd w README głównym: [J3](../../README.pl.md#j3--mock-device-inventory-api-chmura-i-dfu). Zestawy risk-based: [N3](../../README.pl.md#n3--testy-oparte-na-ryzyku-smoke-i-pełna-regresja).

---

## Architektura

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

| Moduł | Odpowiedzialność |
|-------|------------------|
| `models.py` | `DeviceState`, pydantic `Device`, `parse_device` |
| `inventory.py` | Przejścia stanów i DFU |
| `api.py` | Routing HTTP i kody odpowiedzi |

Błędy domeny: `DeviceLabError` w `lab_fw.core.errors`.

---

## Stany i pola

| Pole | Typ | Opis |
|------|-----|------|
| `device_id` | `str` | Unikalny identyfikator |
| `firmware_version` | `str` | Aktualne FW |
| `state` | `DeviceState` | `online`, `offline`, `dfu_in_progress` |
| `last_seen_at` | `datetime \| None` | Ostatni heartbeat (UTC) |

### Tabela przejść

| Stan | Akcja | Nowy stan | Efekty |
|------|-------|-----------|--------|
| — | `register` | `offline` | `last_seen_at = None` |
| `offline` | `heartbeat` | `online` | `last_seen_at = now` |
| `offline` | `set_state(online)` | `online` | bez zmiany `last_seen_at` |
| `online` | `set_state(offline)` | `offline` | — |
| `online` | `start_dfu` | `dfu_in_progress` | FW bez zmian |
| `dfu_in_progress` | `complete_dfu(v)` | `online` | FW = `v` |
| `dfu_in_progress` | `fail_dfu` | `online` | FW bez zmian |
| `dfu_in_progress` | `heartbeat` | `dfu_in_progress` | tylko `last_seen_at` |

`set_state` **nie** wchodzi/wychodzi z DFU.

### Wyjątki

| Wyjątek | Kiedy |
|---------|--------|
| `DeviceNotFoundError` | Nieznane id |
| `InvalidStateTransitionError` | Niedozwolone przejście |
| `DfuAlreadyInProgressError` | Drugi `start_dfu` |
| `SchemaError` | Zły dict w `parse_device` |

---

## HTTP API

URL testowy: `https://device-cloud.test`. Handler: `create_handler(inventory)`.

| HTTP | Path | Body | Efekt |
|------|------|------|--------|
| GET | `/devices` | — | Lista |
| GET | `/devices/{id}` | — | Jedno urządzenie |
| POST | `/devices/{id}/heartbeat` | — | Heartbeat |
| POST | `/devices/{id}/dfu/start` | `{"target_version":"2.0.0"}` | Start DFU |
| POST | `/devices/{id}/dfu/complete` | `{"version":"2.0.0"}` | Complete |
| POST | `/devices/{id}/dfu/fail` | — | Fail DFU |
| POST | `/devices/{id}/dfu/set_state` | `{"state":"online"}` | Admin |

`target_version` nie jest zapisywane w modelu (wersja edukacyjna).

### Błędy JSON

| HTTP | error |
|------|-------|
| 404 | `device_not_found`, `not_found` |
| 409 | `invalid_state_transition` |
| 400 | `invalid_json`, `missing_*`, `invalid_*` |
| 405 | `method_not_allowed` |

---

## Pliki testów

| Plik | Zakres |
|------|--------|
| `test_models.py` | `parse_device` |
| `test_inventory_states.py` | Inventory, DFU, ghost online |
| `test_inventory_api.py` | HTTP + `ApiClient` |

Marker: **`@pytest.mark.device_lab`**.

---

## Polecenia

```bash
pytest tests/device_lab -m device_lab -q
pytest --collect-only -q -m device_lab
pytest tests/device_lab/test_inventory_states.py -v
```

Bez compose / Playwright / Selenium. W CI: `not ui and not selenium and not compose`.

---

## Powiązania

| Rozdział | Powiązanie |
|----------|------------|
| **N3** | slice `-m device_lab` |
| **mocks_lab** | MockTransport |
| **api** | `ApiClient` |
| **distributed_lab** | DFU ≈ praca asynchroniczna; L1 idempotency |

---

## Pułapki przy rozszerzaniu

1. Współdzielone obiekty `Device` w pamięci.
2. FW zmienia się w `complete_dfu`, nie w `start_dfu`.
3. DFU kończ przez `complete_dfu` / `fail_dfu`, nie `set_state`.
4. `online` bez heartbeat → ghost online.
