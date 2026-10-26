# lab_fw reporting

[RU](README.md) · **EN** · [PL](README.pl.md)

Framework reporting layer. Tests and `ApiClient` call this API, not `allure` directly.

## Install

<!-- mod-deep:reporting:install -->
#### About this section — install

`allure-pytest` is in `[dev]`. Without it, decorators and steps are no-ops.

## API

<!-- mod-deep:reporting:api -->
#### About this section — reporting API

Decorators via `decor_allure`: epic/feature/severity/testcase/issue. `ApiClient` already emits steps on HTTP.

## Allure metadata (N1)

<!-- mod-deep:reporting:n1 -->
#### About this section — N1 metadata

`categories.json` plus dynamic `environment.properties` in `tests/conftest.py` (master process only).

## Run with Allure

<!-- mod-deep:reporting:run -->
#### About this section — running

`--alluredir` is required for result files; `allure serve` is local-only.

## TestRail and Jira (N2)

<!-- mod-deep:reporting:n2 -->
#### About this section — N2

Links in Allure ≠ upload to TestRail (trcli). Both are described in root README N2.

## Layer tests

<!-- mod-deep:reporting:tests -->
#### About this section — layer tests

`pytest -m reporting` does not collect the name `testcase` as a test (`python_functions = test_*` in pyproject).

