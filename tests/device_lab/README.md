# Device lab — mock cloud inventory

**RU** · [EN](README.en.md) · [PL](README.pl.md)

Учебный каталог тестов и контракт **облачного inventory** для IoT-сценариев: регистрация устройства, heartbeat, состояния и DFU **без** реального Bluetooth и **без** Docker. Реализация: пакет `device_lab` в `src/device_lab/`.

Корневой обзор: [J3 в README](../../README.md#j3--mock-device-inventory-api-облако-и-dfu). Risk-based наборы: [N3](../../README.md#n3--тестирование-на-основе-рисков-smoke-и-полная-регрессия).

---

## Архитектура

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

| Модуль | Ответственность |
|--------|-----------------|
| `models.py` | `DeviceState`, pydantic-модель `Device`, `parse_device` |
| `inventory.py` | Бизнес-логика переходов и DFU |
| `api.py` | HTTP-маршрутизация и коды ответов |

Ошибки домена наследуют `DeviceLabError` в `lab_fw.core.errors` — единый стиль с API/UI слоями.

---

## Состояния и поля

| Поле | Тип | Описание |
|------|-----|----------|
| `device_id` | `str` | Уникальный идентификатор |
| `firmware_version` | `str` | Текущая версия прошивки |
| `state` | `DeviceState` | `online`, `offline`, `dfu_in_progress` |
| `last_seen_at` | `datetime \| None` | UTC timestamp последнего heartbeat |

### Таблица переходов (источник правды)

| Текущее состояние | Действие | Новое состояние | Побочные эффекты |
|-------------------|----------|-----------------|------------------|
| — | `register` | `offline` | `last_seen_at = None` |
| `offline` | `heartbeat` | `online` | `last_seen_at = now` |
| `offline` | `set_state(online)` | `online` | `last_seen_at` **не** меняется |
| `online` | `set_state(offline)` | `offline` | — |
| `online` | `start_dfu` | `dfu_in_progress` | FW **без** изменений |
| `dfu_in_progress` | `complete_dfu(v)` | `online` | FW = `v`, `last_seen_at = now` |
| `dfu_in_progress` | `fail_dfu` | `online` | FW **без** изменений |
| `dfu_in_progress` | `heartbeat` | `dfu_in_progress` | только `last_seen_at` |

`set_state` **не** меняет состояние из/в `dfu_in_progress`.

### Исключения

| Исключение | Когда |
|------------|--------|
| `DeviceNotFoundError` | Неизвестный `device_id` |
| `InvalidStateTransitionError` | Запрещённый переход (в т.ч. DFU не из `online`) |
| `DfuAlreadyInProgressError` | Второй `start_dfu` |
| `SchemaError` | Невалидный dict в `parse_device` |

---

## HTTP API

Базовый URL в тестах: `https://device-cloud.test`. Handler: `create_handler(inventory)`.

### Успешные операции

| HTTP | Path | Body | Эффект |
|------|------|------|--------|
| GET | `/devices` | — | Массив всех устройств |
| GET | `/devices/{id}` | — | Один объект `Device` |
| POST | `/devices/{id}/heartbeat` | — | Heartbeat |
| POST | `/devices/{id}/dfu/start` | `{"target_version":"2.0.0"}` | Start DFU |
| POST | `/devices/{id}/dfu/complete` | `{"version":"2.0.0"}` | Complete DFU |
| POST | `/devices/{id}/dfu/fail` | — | Fail DFU |
| POST | `/devices/{id}/dfu/set_state` | `{"state":"online"}` | Admin `set_state` |

`target_version` в учебной модели **не сохраняется** в объекте устройства — проверяется только допустимость перехода.

### Коды ошибок (JSON `{"error": "…"}`)

| HTTP | error | Смысл |
|------|-------|--------|
| 404 | `device_not_found` | Нет устройства |
| 404 | `not_found` | Неверный path |
| 409 | `invalid_state_transition` | Конфликт состояния / DFU |
| 400 | `invalid_json`, `missing_*`, `invalid_*` | Тело запроса |
| 405 | `method_not_allowed` | Неподдерживаемый метод |

---

## Структура тестов

| Файл | Фокус |
|------|--------|
| `test_models.py` | `parse_device`, pydantic strict |
| `test_inventory_states.py` | `InMemoryInventory`, переходы, DFU, ghost online |
| `test_inventory_api.py` | HTTP + `ApiClient`, негативы, routing |

Маркер: **`@pytest.mark.device_lab`** (описание в `pyproject.toml`).

---

## Команды

```bash
# Все тесты device lab
pytest tests/device_lab -m device_lab -q

# Инвентаризация (число тестов для N3-матрицы)
pytest --collect-only -q -m device_lab

# Один файл
pytest tests/device_lab/test_inventory_states.py -v
```

Тесты **не** требуют `compose`, Playwright или Selenium. Они входят в прогон workflow **tests** (`not ui and not selenium and not compose`).

---

## Связь с другими разделами

| Раздел | Связь |
|--------|--------|
| **N3** | `-m device_lab` — отдельный slice inventory/cloud; комбинируется с `-m smoke` на части кейсов |
| **mocks_lab** | Тот же MockTransport + handler pattern |
| **api** | `ApiClient`, `Settings`, JSON responses |
| **distributed_lab** | Аналогия: долгий DFU ≈ async job; не retry POST без idempotency (L1) |

---

## Типичные ошибки при расширении

1. **Мутация shared Device** — объекты хранятся in-memory; тесты должны понимать, что `get` возвращает тот же экземпляр.
2. **Ожидание смены FW в `start_dfu`** — версия меняется только в `complete_dfu`.
3. **Сброс DFU через `set_state`** — запрещено; используй `complete_dfu` / `fail_dfu`.
4. **Путать online и heartbeat** — online без `last_seen_at` возможен (ghost online).
