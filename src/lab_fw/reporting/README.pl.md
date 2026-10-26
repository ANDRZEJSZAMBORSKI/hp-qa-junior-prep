# lab_fw reporting

[RU](README.md) · [EN](README.en.md) · **PL**

Warstwa raportowania frameworka. Testy i `ApiClient` wołają to API, a nie `allure` bezpośrednio.

## Instalacja

<!-- mod-deep:reporting:install -->
#### O sekcji — instalacja

`allure-pytest` w `[dev]`. Bez niego dekoratory i steps są no-op.

## API

<!-- mod-deep:reporting:api -->
#### O sekcji — API reporting

Dekoratory przez `decor_allure`: epic/feature/severity/testcase/issue. `ApiClient` już emituje steps przy HTTP.

## Metadane Allure (N1)

<!-- mod-deep:reporting:n1 -->
#### O sekcji — metadane N1

`categories.json` + dynamiczne `environment.properties` w `tests/conftest.py` (tylko proces master).

## Uruchomienie z Allure

<!-- mod-deep:reporting:run -->
#### O sekcji — uruchomienie

`--alluredir` jest wymagany dla plików; `allure serve` tylko lokalnie.

## TestRail i Jira (N2)

<!-- mod-deep:reporting:n2 -->
#### O sekcji — N2

Linki w Allure ≠ upload do TestRail (trcli). Oba opisane w README głównym N2.

## Testy warstwy

<!-- mod-deep:reporting:tests -->
#### O sekcji — testy warstwy

`pytest -m reporting` — nie zbiera nazwy `testcase` jako testu (`python_functions = test_*` w pyproject).

