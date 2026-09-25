# lab_fw pytest plugin

[RU](README.md) · **EN** · [PL](README.pl.md)

Pytest plugin for the `lab_fw` package: failure logging and optional text artifacts.

## Install

```bash
pip install -e ".[dev]"
```

After install, pytest loads the plugin via the `pytest11` entry point (`lab_fw`).

Check:

```bash
pytest --trace-config -q
```

You should see `lab-fw` among plugins.

## Flags

| Flag | Purpose |
|------|---------|
| `--lab-fw-artifacts` | Write a text file on failure |
| `--lab-fw-artifacts-dir DIR` | Artifacts directory (default: `.lab_fw_artifacts`) |

Without `--lab-fw-artifacts`, only an `ERROR` log on logger `lab_fw.pytest` is written.

## On failure

When a test fails in the `call` phase:

1. always: `FAILED <nodeid>: <error>` to the log;
2. with `--lab-fw-artifacts`: a file in the chosen directory (`nodeid` + traceback).

## Examples

```bash
pytest -q
pytest -q --lab-fw-artifacts
pytest -q --lab-fw-artifacts --lab-fw-artifacts-dir=./my_artifacts
```

## Plugin tests

```bash
pytest -q tests/test_pytest_plugin.py
```
