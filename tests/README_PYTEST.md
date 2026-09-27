# Pytest notes (lab_fw)

**RU** · [EN](README_PYTEST.en.md) · [PL](README_PYTEST.pl.md)

Короткие правила изоляции и hygiene для этого репо.

## Fixture scopes

| Scope | Когда |
|-------|--------|
| `function` (default) | почти всегда: клиент, транспорт, временные данные |
| `module` | дорогой неизменяемый setup на файл |
| `session` | редко; легко сломать xdist shared state |

`api_client` в корневом `conftest`: `yield` → `close()` (как context manager).

## conftest hierarchy

- `tests/conftest.py` — общее (settings, logging, `api_client`)
- `tests/mocks_lab/conftest.py` — только для поддерева `mocks_lab/` (например `mock_handler`)

Локальный conftest не «виден» тестам вне своей папки.

## xdist

```bash
pytest -q -n auto
```

Плохо: глобальный mutable (`list`/`dict` на уровне модуля), общий файл/порт без изоляции, зависимость от порядка тестов.  
Хорошо: состояние в fixture с `yield`, MockTransport вместо сети, каждый тест сам себе окружение.

Демо: `tests/test_xdist_isolation.py` (плохой кейс помечен `skip`).

## Anti-flaky checklist

1. Тесты не зависят от порядка.
2. Нет shared mutable между тестами.
3. Unit без реальной сети — mock / MockTransport.
4. Не использовать `sleep` как условие успеха.
5. Под `-n auto` suite должен быть зелёным так же, как без него.

## Полезные команды

```bash
pytest -q
pytest -q -n auto
pytest -q tests/test_fixtures_scopes.py
pytest -q tests/test_xdist_isolation.py
```
