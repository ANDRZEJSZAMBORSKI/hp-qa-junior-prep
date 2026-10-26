# lab_fw reporting

**RU** · [EN](README.en.md) · [PL](README.pl.md)

<!-- mod-preamble -->

### О модуле reporting

Фасад над Allure: тесты не импортируют `allure` напрямую — проще no-op без `allure-pytest` и единый стиль steps/attachments. См. корневой **N1–N2**.

## Установка

<!-- mod-deep:reporting:install -->
### О разделе — установка

`allure-pytest` в `[dev]`. Без него декораторы и steps — no-op.

## API

<!-- mod-deep:reporting:api -->
### О разделе — API reporting

Декораторы через `decor_allure`: epic/feature/severity/testcase/issue. `ApiClient` уже emit steps при HTTP.

## Метаданные Allure (N1)

<!-- mod-deep:reporting:n1 -->
### О разделе — метаданные N1

`categories.json` + dynamic `environment.properties` в `tests/conftest.py` (master process only).

## Прогон с Allure

<!-- mod-deep:reporting:run -->
### О разделе — прогон

`--alluredir` обязателен для файлов; `allure serve` только локально.

## TestRail и Jira (N2)

<!-- mod-deep:reporting:n2 -->
### О разделе — N2

Links в Allure ≠ upload в TestRail (trcli). Оба описаны в корневом README N2.

## Тесты слоя

<!-- mod-deep:reporting:tests -->
### О разделе — тесты слоя

`pytest -m reporting` — не собирает имя `testcase` как тест (`python_functions = test_*` в pyproject).

