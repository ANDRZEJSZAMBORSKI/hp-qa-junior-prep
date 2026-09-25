# lab_fw pytest plugin

[RU](README.md) · [EN](README.en.md) · **PL**

Plugin pytest pakietu `lab_fw`: log przy failu i opcjonalne artefakty tekstowe.

## Instalacja

```bash
pip install -e ".[dev]"
```

Po instalacji pytest ładuje plugin przez entry point `pytest11` (`lab_fw`).

Sprawdzenie:

```bash
pytest --trace-config -q
```

Na liście plugins powinno być `lab-fw`.

## Flagi

| Flaga | Znaczenie |
|-------|-----------|
| `--lab-fw-artifacts` | Zapisz plik tekstowy przy failu |
| `--lab-fw-artifacts-dir DIR` | Katalog artefaktów (domyślnie: `.lab_fw_artifacts`) |

Bez `--lab-fw-artifacts` zapisuje się tylko log `ERROR` na loggerze `lab_fw.pytest`.

## Przy failu

Gdy test padnie w fazie `call`:

1. zawsze: `FAILED <nodeid>: <błąd>` do logu;
2. z `--lab-fw-artifacts`: plik w wybranym katalogu (`nodeid` + traceback).

## Przykłady

```bash
pytest -q
pytest -q --lab-fw-artifacts
pytest -q --lab-fw-artifacts --lab-fw-artifacts-dir=./my_artifacts
```

## Testy pluginu

```bash
pytest -q tests/test_pytest_plugin.py
```
