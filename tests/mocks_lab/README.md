# Mocks lab

**RU** · [EN](README.en.md) · [PL](README.pl.md)

<!-- mod-preamble -->

### О модуле mocks_lab

Учебный **каталог паттернов** подмены: от `unittest.mock` до `httpx.MockTransport`. Связан с **I2** и [API README](../../../src/lab_fw/api/README.md).

## Как запускать

<!-- mod-deep:mocks_lab:run -->
### О разделе — запуск

Фильтры `mocks_pure` / `mocks_httpx` делят Part I и II без ручного перечисления файлов.

## Структура

<!-- mod-deep:mocks_lab:structure -->
### О разделе — структура

Два transport-файла намеренно дублируют идеи — сравни fixture vs ручной Settings.

## Часть I — чистые моки

<!-- mod-deep:mocks_lab:pure -->
### О разделе — чистые моки

Patch на «не том шве» — частая ошибка junior. Спрашивай себя: подменяем **клиент**, **метод** или **transport**?

## Часть II — `httpx.MockTransport`

<!-- mod-deep:mocks_lab:transport -->
### О разделе — MockTransport

Предпочтительный стиль для `ApiClient(settings, transport=...)`. Handler видит real `httpx.Request`.

## Когда что выбирать (шпаргалка)

<!-- mod-deep:mocks_lab:cheatsheet -->
### О разделе — шпаргалка

Используй таблицу при code review: transport для контракта HTTP, mock для узкой ветки логики.

## Связь с `lab_fw`

<!-- mod-deep:mocks_lab:tiein -->
### О разделе — связь с lab_fw

Логи retry уже в conftest — смотри WARNING при `pytest -v tests/mocks_lab`.

