Репозиторий **hp-qa-junior-prep** — это учебно-практический проект автоматизации QA на Python. Здесь собран воспроизводимый стек: пакет **`lab_fw`** (HTTP-клиент, UI, конфигурация, reporting, pytest-плагин), набор **pytest**-тестов, **Docker / Compose**, **GitHub Actions** и отчёты **Allure**. Внешний «боевой» API в типичных прогонах **не вызывается**: контракт имитируют **MockTransport** и **MockServer**, чтобы отрабатывать изоляцию, интеграцию и диагностику без зависимости от сети.

Документ ниже одновременно **инструкция** (команды, env, CI) и **учебник** (теория, связь с кодом, типичные ошибки). Три языка: **RU** (этот файл), [EN](README.en.md), [PL](README.pl.md).

### Для кого

- Инженер QA / SDET, который поднимает фреймворк локально и в CI.
- Разработчик, которому нужно понять, как устроены моки, параллельный pytest и traceability (TestRail / Jira).

### Что вы получите после прохождения материала

- Умение выбирать уровень теста: in-process mock vs контейнерный MockServer vs UI в Grid/Docker.
- Понимание retry, timeout, deadline, idempotency на примере `ApiClient` и `Worker`.
- Навык расследования падений: env → build → logs → metrics → trace.
- Практику Allure + опциональную связь с TestRail и Jira.

### Требования

| Компонент | Версия / примечание |
|-----------|---------------------|
| Python | **≥ 3.11** (`pyproject.toml`) |
| Git | для клонирования и воспроизведения commit в CI |
| Docker Desktop (опционально) | Compose-тесты, Grid, Playwright в CI-образе |
| Allure CLI (опционально) | `allure serve` локально |
| TestRail CLI (опционально) | канал B в разделе N2 |

### Карта разделов документа

| Блок | Тема | Где в коде |
|------|------|------------|
| **I1–I4** | API, моки, негативы, диагностика | `tests/mocks_lab/`, `tests/test_compose_api.py`, `src/lab_fw/api/` |
| **L1–L3** | Распределённые системы, очередь/worker, расследование | `src/distributed_lab/`, `tests/distributed_lab/` |
| **M1–M2** | xdist, изоляция, Selenium Grid, UI в Docker | `tests/parallel_lab/`, `tests/conftest.py`, Compose profiles |
| **N1–N3** | Allure, TestRail, Jira, risk-based наборы | `src/lab_fw/reporting/`, `tests/test_api_client.py`, `pyproject.toml` (markers) |
| **J3** | Mock Device Inventory (cloud, DFU, heartbeat) | `src/device_lab/`, `tests/device_lab/` |

Рекомендуемый порядок чтения: **Быстрый старт → Структура → I1–I4 → L1 → L2 → L3 → M1 → M2 → N1 → N2 → N3 → J3**. Разделы Docker и GitHub Actions удобно держать под рукой при любом прогоне.

### Содержание

1. [Быстрый старт](#быстрый-старт-локально)
2. [Структура репозитория](#структура)
3. [Переменные окружения](#переменные-окружения)
4. [Маркеры pytest](#маркеры-pytest)
5. [Docker](#docker)
6. [GitHub Actions](#github-actions)
7. [I1 — схема API](#схема-взаимодействия-api-i1) (включая I2–I4)
8. [L1 — глоссарий](#распределённые-системы-теория-и-термины-l1)
9. [L2 — очередь и worker](#l2--очередь-retry-timeout-deadline-idempotency)
10. [L3 — расследование сбоев](#l3--расследование-сбоев-чек-лист)
11. [M1 — параллельность](#m1--параллельное-выполнение-и-изоляция-ресурсов)
12. [M2 — Grid и UI](#m2--удалённый-браузер-selenium-grid-и-ui-в-docker)
13. [N1 — Allure](#n1--отчёты-allure)
14. [N2 — TestRail и Jira](#n2--jira--testrail)
15. [N3 — risk-based (smoke / full)](#n3--тестирование-на-основе-рисков-smoke-и-полная-регрессия)
16. [J3 — Device Inventory API (облако и DFU)](#j3--mock-device-inventory-api-облако-и-dfu)
17. [Allure (кратко)](#allure-кратко)
18. [Документация модулей](#документация-модулей)

### Как читать каждый раздел

В начале главы — блок **«О разделе»**: зачем тема, что смотреть в репозитории, как проверить себя. Дальше — справочные таблицы, команды и связь с тестами. Если команда падает, сначала [I4](#диагностика-падения-тестов-i4), затем при сбоях инфраструктуры — [L3](#l3--расследование-сбоев-чек-лист).
