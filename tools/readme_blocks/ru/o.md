### О разделе

**O** — надёжность automation: **контролируемый retry** в HTTP-клиенте, **anti-flaky** hygiene, **quality gates** в GitHub Actions и **AI-assisted** разработка с обязательной верификацией. Материал опирается на код `lab_fw`, workflow `.github/workflows/` и [tests/README_PYTEST.md](tests/README_PYTEST.md).

Связанные главы: [L1](#распределённые-системы-теория-и-термины-l1) (retry ≠ timeout), [L2](#l2--очередь-retry-timeout-deadline-idempotency) (worker), [L3](#l3--расследование-сбоев-чек-лист), [N3](#n3--тестирование-на-основе-рисков-smoke-и-полная-регрессия) (наборы и CI), [M1](#m1--параллельное-выполнение-и-изоляция-ресурсов) (xdist, `serial`), [J3](#j3--mock-device-inventory-api-облако-и-dfu) (POST DFU без слепого retry).

---

### O1 — Политика retry (HTTP-клиент)

**Источник правды:** `src/lab_fw/api/retry_policy.py` → `should_retry(exc)`; оркестрация — `src/lab_fw/core/retry.py` → `retry_call`.

| Ситуация | Retry? |
|----------|--------|
| **GET** + HTTP **429**, **503** | Да |
| **GET** + HTTP 400, 401, 404, 422, **500**, … | Нет |
| **GET** + transport (ConnectError, ReadTimeout, …) | Да |
| **POST** + любой status или transport | **Нет** |

**Зачем POST не retry:** сервер мог уже выполнить операцию; повтор создаёт **дублирующий side effect** (запись, платёж, второй `start_dfu`). Для POST после timeout нужны **idempotency** и явная политика (см. L2), а не слепой цикл.

**GET + 500 не retry:** это ответ о **внутренней ошибке** приложения; повторы маскируют дефект и нагружают систему. Retry только на **transient** (503, 429, сеть).

**429:** политика разрешает retry на GET; в production учитывают **`Retry-After`**; в учебном клиенте пауза задаётся **backoff + jitter** в `retry_call`, без парсинга заголовка.

**Параметры `retry_call`:**

- `attempts=3` — три вызова `fn()` всего (первая попытка + два повтора).
- `retry_if=True` — перед повтором вызывается **`should_retry`**; при `retry_if=False` возможен «слепой» retry по `retry_on` (опасно для POST).
- После исчерпания попыток пробрасывается **последнее** исключение — успех не подменяется.

```bash
pytest tests/test_api_retry_policy.py -m api -q
pytest tests/test_api_retry_policy.py -v -k "503" --log-cli-level=WARNING
```

**Retry клиента ≠ pytest-rerun:** `pytest-rerunfailures` на весь suite может скрыть flaky или настоящий баг; flaky лечат через **O2**, не глобальным rerun.

---

### O2 — Anti-flaky и quarantine

Чеклист: [tests/README_PYTEST.md](tests/README_PYTEST.md) → **Anti-flaky checklist**.

1. Тесты **не зависят от порядка** выполнения.
2. **Нет shared mutable state** между тестами (общие list/dict на уровне модуля, один файл без изоляции).
3. Unit/API **без реальной сети** — MockTransport / mock handler.
4. **Не `sleep`** как условие успеха — ожидание **состояния** с timeout (элемент UI, статус job, JSON ответа).
5. Suite **зелёный** и без `-n auto`, и с **`pytest -q -n auto`**.

**xdist:** каждый worker — отдельный процесс; предпочтительно **уникальный** файл/запись/fixture на тест; если общий ресурс неизбежен — **FileLock** (`tests/parallel_lab/`, M1) или **`@pytest.mark.xdist_group`**. Маркер **`serial`** — тесты, которые нельзя безопасно гонять параллельно с другими; фактический режим задаёт **команда pytest** (не смешивать `serial` UI с `-n auto` без группы).

**Quarantine (процесс):** воспроизвести → логи / Allure → root cause → fix; если fix не сразу — **`@pytest.mark.skip(reason=…)`** + issue, **не** `--reruns 10` на весь CI.

```bash
pytest -q -n auto
pytest tests/parallel_lab -m parallel_lab -n 2 -q
```

---

### O3 — Quality gates в CI

Два уровня gate (см. [GitHub Actions](#github-actions)):

| Workflow | Runner | Что проверяет |
|----------|--------|----------------|
| **`tests.yml`** | `ubuntu-latest`, pip | `pytest -m "not ui and not selenium and not compose" -q -n auto`, секрет `LAB_FW_API_TOKEN`, Allure artifact |
| **`ci.yml`** | Docker Compose | `mock-api`, compose-тесты, Selenium и Playwright (parallel + **serial**), cleanup `if: always()` |

**Shift-left:** шаг **Check secret** падает **до** pytest, если токен пустой.

**CI-filter (tests.yml):** включает API, mocks, `distributed_lab`, `parallel_lab`, **`device_lab`**, reporting — **исключает** `ui`, `selenium`, `compose` (нужны браузер / MockServer в контейнере).

**Smoke (`-m smoke`, ~17 тестов)** — быстрый локальный сигнал; **не** заменяет CI-filter (~**391** тест). **Полная коллекция** — ~**476** (пересчёт: `pytest --collect-only -q`).

**`if: always()`** на upload Allure — артеfact для расследования при **красном** job; статус job остаётся failed.

Локальная симуляция PR gate:

```bash
pytest -m "not ui and not selenium and not compose" -q -n auto --tb=line
```

---

### O4 — AI-assisted development

Рекомендуемый цикл:

1. **Требования и ограничения** (контракт API, «не менять тесты без согласования»).
2. **Агент** (например Cursor): scaffold, docs, поиск по репо, черновики.
3. **Review diff** — домен, security, стиль, соответствие `lab_fw`.
4. **pytest** локально; для крупных изменений — **CI-filter**; при необходимости — полный **`ci.yml`** локально через Compose.
5. **Merge** только после review и зелёного gate; flaky — **O2**, не ослабление CI.

AI ускоряет черновики; **качество** обеспечивают тесты, логи и ваш review — как для любого PR.

---

### Сводная таблица

| Тема | Ключевые файлы / команды |
|------|---------------------------|
| Retry | `retry_policy.py`, `test_api_retry_policy.py` |
| Flaky | `tests/README_PYTEST.md`, `test_xdist_isolation.py`, `parallel_lab` |
| Gates | `.github/workflows/tests.yml`, `ci.yml`, N3 |
| AI | Review + pytest + Actions |

### Самопроверка

1. Назовите три случая, когда **GET** retry, и один, когда **POST** не retry.
2. Чем **smoke** отличается от фильтра **tests.yml**?
3. Зачем **`distributed_lab`** в CI-filter, а **`compose`** — нет?
4. Почему **`upload-artifact: if: always()`** не делает job зелёным?
5. Одним абзацем: ваш workflow с AI от ТЗ до merge.
