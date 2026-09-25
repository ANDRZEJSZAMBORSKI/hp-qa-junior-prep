# lab_fw pytest plugin

**RU** · [EN](README.en.md) · [PL](README.pl.md)

Pytest plugin пакета `lab_fw`: лог и опциональные текстовые артефакты при падении теста.

## Установка

```bash
pip install -e ".[dev]"
```

После установки pytest подхватывает plugin через entry point `pytest11` (`lab_fw`).

Проверка:

```bash
pytest --trace-config -q
```

В списке plugins должно быть `lab-fw`.

## Флаги

| Флаг | Назначение |
|------|------------|
| `--lab-fw-artifacts` | Писать текстовый файл при fail |
| `--lab-fw-artifacts-dir DIR` | Каталог артефактов (default: `.lab_fw_artifacts`) |

Без `--lab-fw-artifacts` пишется только лог `ERROR` в logger `lab_fw.pytest`.

## Поведение на fail

На фазе `call`, если тест упал:

1. всегда: `FAILED <nodeid>: <ошибка>` в лог;
2. с `--lab-fw-artifacts`: файл в указанном каталоге (`nodeid` + traceback).

## Примеры

```bash
pytest -q
pytest -q --lab-fw-artifacts
pytest -q --lab-fw-artifacts --lab-fw-artifacts-dir=./my_artifacts
```

## Тесты plugin

```bash
pytest -q tests/test_pytest_plugin.py
```
