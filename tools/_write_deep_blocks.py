# Run once: python tools/_write_deep_blocks.py
from pathlib import Path

ROOT = Path(__file__).parent
L1 = ROOT / "l1_deep_blocks"
MOD = ROOT / "module_deep_blocks"


def w(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


L1_RU = {
1: """#### О пункте 1 — Async communication

**Смысл:** вызывающий код не блокируется на полной обработке; результат обрабатывается позже другим компонентом.

**В репозитории:** очередь `InMemoryQueue` + `Worker.run_once()` — положили `Job`, HTTP выполнится при следующем `run_once`, а не в момент `put`.

```python
# src/distributed_lab/queue_worker.py (идея)
queue.put(job)
worker.run_once()  # один job → HTTP через ApiClient
```

**QA:** тестируй «принято к обработке» и «итоговое состояние» отдельно; не смешивай с «fire-and-forget без проверки».

**Проверка:** `pytest tests/distributed_lab/test_queue_worker.py -q`
""",
2: """#### О пункте 2 — Queue / event / broker

**В репозитории:** упрощённая **Queue** — FIFO на `deque`, типизированный `Job` (`parse_job` → `SchemaError` при битой схеме).

```python
# src/distributed_lab/queue_worker.py
class InMemoryQueue:
    def put(self, job: Job) -> None: ...
    def get(self) -> Job | None: ...
```

**Event** в проде — факт домена (`OrderCreated`); здесь аналог — dict job, который валидируется в модель.

**QA:** после `put` job не теряется; повторная обработка смотри в пункте 5 (idempotency).

**Проверка:** `pytest tests/distributed_lab/test_queue_worker.py -k queue -q`
""",
3: """#### О пункте 3 — Retry vs timeout

**Retry** решает «повторять ли после ошибки»; **timeout** — «сколько ждать одну попытку». После timeout исход на сервере **неизвестен** — повтор POST опасен без idempotency.

**Политика в коде** (`src/lab_fw/api/retry_policy.py`):

```python
def should_retry(exc: ApiError) -> bool:
    # GET + 429/503 или GET + transport error → True
    # POST → False
```

**Оркестрация:** `lab_fw.core.retry.retry_call` вызывает `should_retry` между попытками.

**Проверка:** `pytest tests/test_api_retry_policy.py tests/distributed_lab/test_l3_investigation.py -q`
""",
4: """#### О пункте 4 — Timeout

**Уровни timeout в репо:**

| Уровень | Где |
|---------|-----|
| HTTP client | `Settings.timeout_s` → `ApiClient` |
| Compose негатив | `timeout_s=0.2` vs delay 1000 ms в MockServer (`tests/test_compose_api.py`) |
| Job / worker | `Job.timeout`, `Job.deadline_s`, `Worker.deadline_w` → `JobDeadlineExceeded` |

```python
# Worker.execute — минимум из job timeout и оставшегося deadline
timeout = min(job.timeout, remaining, remaining_worker)
```

**QA:** assert на тип ошибки: `ApiError` + `__cause__` is `ReadTimeout`, не только «упало».

**Проверка:** `pytest tests/test_compose_api.py::test_mock_api_timeout tests/distributed_lab/test_timeout.py -q`
""",
5: """#### О пункте 5 — Idempotency

**Заголовок на wire** (без мутации модели job):

```python
# src/distributed_lab/queue_worker.py
if job.idempotency_key is not None:
    kwargs["headers"]["Idempotency-Key"] = job.idempotency_key
```

**Тестовый сервер** в `tests/distributed_lab/test_timeout.py`: повторный POST с тем же ключом не увеличивает `received_requests`.

**Политика retry:** POST **не** ретраится в `should_retry` / worker — защита от двойного эффекта.

**Проверка:** `pytest tests/distributed_lab/test_timeout.py -q -k idempotency`
""",
6: """#### О пункте 6 — Eventual consistency

**Идея:** состояние систем может кратко расходиться; тест ждёт согласования с **deadline**, а не фиксированным `sleep`.

**В репо:** worker проверяет оставшееся время через `_remaining_time` перед и после HTTP; UI-слой использует explicit waits (`PlaywrightWait` / `SeleniumWait`) вместо слепой паузы.

**QA-паттерн:**

```python
# анти-паттерн: time.sleep(5)
# лучше: wait с timeout из settings (ui_timeout_s / job deadline)
```

**Проверка:** `pytest tests/test_playwright_wait.py tests/test_selenium_wait.py -q`
""",
7: """#### О пункте 7 — Logs / metrics / traces

| Сигнал | Пример в репо |
|--------|----------------|
| **Logs** | `INFO lab_fw.api`, `WARNING lab_fw.core.retry` при retry |
| **Metrics** | ручные counters в L3: `http_requests`, `503_count` |
| **Traces** | нет полного OTel; есть wire ID `X-Request-ID` (п. 8) |

**Практика L3:** `caplog` ловит два WARNING перед успешным retry на 503.

**Проверка:** `pytest tests/distributed_lab/test_l3_investigation.py -q`
""",
8: """#### О пункте 8 — Correlation / Request / Trace ID

**В репо:** job передаёт заголовки как есть — тесты задают `X-Request-ID`:

```python
# tests/distributed_lab/test_timeout.py — job headers на HTTP
headers={"X-Request-ID": "req-123"}
```

**Retry:** каждая попытка GET может повторить тот же `Idempotency-Key`; Request ID политика зависит от API (здесь — то, что положили в job).

**QA:** grep по репо: `grep -Rni "X-Request-ID" src tests`

**Проверка:** `pytest tests/distributed_lab/test_timeout.py -q -k request`
""",
9: """#### О пункте 9 — Env vs build

**Env (пример L3):** локально `LAB_FW_API_TOKEN` может быть пуст; в CI workflow **tests** secret **обязателен**.

**Build:** `git rev-parse HEAD`, editable `lab-fw`, Docker image target `ci` vs `local` (Avast CA).

```bash
python -c "import os; print(os.getenv('LAB_FW_API_TOKEN', 'MISSING'))"
docker compose config | head
```

**QA:** падение только в CI → сначала diff env и команды pytest в `.github/workflows/`, не «переписывать тест».

**Проверка:** прочитай `tests/distributed_lab/test_l3_investigation.py` (секции env/build).
""",
}

def _en(text: str) -> str:
    """Reuse RU block structure with EN section titles (body kept bilingual-friendly)."""
    return text.replace("#### О пункте", "#### About item").replace("**Смысл:**", "**Meaning:**").replace(
        "**В репозитории:**", "**In this repo:**"
    ).replace("**QA:**", "**QA:**").replace("**Проверка:**", "**Check:**").replace(
        "**Уровни timeout в репо:**", "**Timeout layers:**"
    ).replace("**Идея:**", "**Idea:**").replace("**QA-паттерн:**", "**QA pattern:**").replace(
        "**Политика в коде**", "**Policy in code**"
    ).replace("**Оркестрация:**", "**Orchestration:**").replace("**Заголовок на wire**", "**Header on the wire**"
    ).replace("**Тестовый сервер**", "**Test server**").replace("**Политика retry:**", "**Retry policy:**")


L1_EN = {n: _en(L1_RU[n]) for n in L1_RU}

L1_PL = {
1: """#### O punkcie 1 — Async communication

**Sens:** kod nie czeka na pełną obsługę; worker wykona HTTP później.

**W repo:** `InMemoryQueue` + `Worker.run_once()` — `put(job)`, potem `run_once()`.

```python
queue.put(job)
worker.run_once()
```

**QA:** sprawdzaj osobno „przyjęto” i stan końcowy.

**Sprawdzenie:** `pytest tests/distributed_lab/test_queue_worker.py -q`
""",
2: L1_EN[2].replace("About item", "O punkcie"),
3: L1_EN[3].replace("About item", "O punkcie"),
4: L1_EN[4].replace("About item", "O punkcie"),
5: L1_EN[5].replace("About item", "O punkcie"),
6: L1_EN[6].replace("About item", "O punkcie"),
7: L1_EN[7].replace("About item", "O punkcie"),
8: L1_EN[8].replace("About item", "O punkcie"),
9: L1_EN[9].replace("About item", "O punkcie"),
}


def write_l1():
    for n, text in L1_RU.items():
        w(L1 / "ru" / f"{n:02d}.md", text)
    for n, text in L1_EN.items():
        w(L1 / "en" / f"{n:02d}.md", text)
    for n, text in L1_PL.items():
        w(L1 / "pl" / f"{n:02d}.md", text)


# Module preambles and section blocks (RU); EN/PL shorter mirrors generated below
def write_modules():
    api_ru = {
        "00_preamble": """### О модуле API

Пакет `lab_fw.api` — HTTP-клиент с явной политикой ошибок, optional Bearer, pydantic-схемами и **opt-in** retry. Документ связан с корневым README **I1–I3** и [mocks_lab](../../../tests/mocks_lab/README.md).

**Файлы:** `client.py`, `auth.py`, `schemas.py`, `retry_policy.py`.""",
        "install": """### О разделе — установка

Editable install подтягивает `httpx`, `pydantic` (dev). Без `[dev]` часть тестов недоступна.""",
        "settings": """### О разделе — Settings

`get_settings()` читает env один раз за процесс; см. корневой README «Переменные окружения». Token опционален — многие тесты используют MockTransport без Bearer.""",
        "bearer": """### О разделе — Bearer

Заголовок ставится при создании клиента, если `api_token` задан. Обновление токена после OAuth — `set_bearer_token`.""",
        "oauth": """### О разделе — client credentials

Демо OAuth без IdP: `fetch_client_credentials_token` → POST `/oauth/token` через тот же `ApiClient` (мокается transport).

**Проверка:** `pytest tests/test_api_auth.py -q`""",
        "schema": """### О разделе — Schema

`parse_user` / `parse_token` централизуют валидацию JSON → `SchemaError` вместо KeyError в каждом тесте.

**Проверка:** `pytest tests/test_api_schemas.py -q`""",
        "negative": """### О разделе — Negative / errors

4xx/5xx **не** exception по умолчанию — явный контракт. Transport → `ApiError` с `__cause__`.

**Проверка:** `pytest tests/test_api_negative.py tests/test_compose_api.py -q`""",
        "retry": """### О разделе — Retry policy

Retry только через `retry_call`, не внутри каждого `get`. Таблица ниже — источник истины для L1 п.3 и L2 worker.

**Проверка:** `pytest tests/test_api_retry_policy.py -q`""",
        "tests": """### О разделе — тесты API

Запускай по файлам при локализации регрессии; `-m api` — весь маркированный набор.""",
    }
    for k, v in api_ru.items():
        w(MOD / "api" / "ru" / f"{k}.md", v)

    # EN api — mirror keys
    api_en = {k: v.replace("### О", "### About").replace("разделе", "section") for k, v in api_ru.items()}
    api_en["00_preamble"] = """### About the API module

`lab_fw.api` — HTTP client with explicit errors, optional Bearer, pydantic schemas, opt-in retry. See root README I1–I3 and [mocks_lab](../../../tests/mocks_lab/README.en.md)."""
    for k, v in api_en.items():
        w(MOD / "api" / "en" / f"{k}.md", v)

    api_pl = {k: v.replace("### О разделе", "### O sekcji").replace("### О модуле API", "### O module API") for k, v in api_ru.items()}
    api_pl["00_preamble"] = """### O module API

Pakiet `lab_fw.api` — klient HTTP, błędy, Bearer, schematy pydantic, retry opt-in. README główne I1–I3, [mocks_lab](../../../tests/mocks_lab/README.pl.md)."""
    for k, v in api_pl.items():
        w(MOD / "api" / "pl" / f"{k}.md", v)

    rep_ru = {
        "00_preamble": """### О модуле reporting

Фасад над Allure: тесты не импортируют `allure` напрямую — проще no-op без `allure-pytest` и единый стиль steps/attachments. См. корневой **N1–N2**.""",
        "install": """### О разделе — установка

`allure-pytest` в `[dev]`. Без него декораторы и steps — no-op.""",
        "api": """### О разделе — API reporting

Декораторы через `decor_allure`: epic/feature/severity/testcase/issue. `ApiClient` уже emit steps при HTTP.""",
        "n1": """### О разделе — метаданные N1

`categories.json` + dynamic `environment.properties` в `tests/conftest.py` (master process only).""",
        "run": """### О разделе — прогон

`--alluredir` обязателен для файлов; `allure serve` только локально.""",
        "n2": """### О разделе — N2

Links в Allure ≠ upload в TestRail (trcli). Оба описаны в корневом README N2.""",
        "tests": """### О разделе — тесты слоя

`pytest -m reporting` — не собирает имя `testcase` как тест (`python_functions = test_*` в pyproject).""",
    }
    for k, v in rep_ru.items():
        w(MOD / "reporting" / "ru" / f"{k}.md", v)
    for lang, trans in (("en", "About"), ("pl", "O sekcji")):
        for k, v in rep_ru.items():
            t = v.replace("### О разделе", f"### {trans}").replace("### О модуле reporting", f"### {trans} module reporting")
            if k == "00_preamble" and lang == "en":
                t = "### About the reporting module\n\nAllure facade; see root N1–N2."
            if k == "00_preamble" and lang == "pl":
                t = "### O module reporting\n\nFasada Allure; README główne N1–N2."
            w(MOD / "reporting" / lang / f"{k}.md", t)

    mocks_ru = {
        "00_preamble": """### О модуле mocks_lab

Учебный **каталог паттернов** подмены: от `unittest.mock` до `httpx.MockTransport`. Связан с **I2** и [API README](../../../src/lab_fw/api/README.md).""",
        "run": """### О разделе — запуск

Фильтры `mocks_pure` / `mocks_httpx` делят Part I и II без ручного перечисления файлов.""",
        "structure": """### О разделе — структура

Два transport-файла намеренно дублируют идеи — сравни fixture vs ручной Settings.""",
        "pure": """### О разделе — чистые моки

Patch на «не том шве» — частая ошибка junior. Спрашивай себя: подменяем **клиент**, **метод** или **transport**?""",
        "transport": """### О разделе — MockTransport

Предпочтительный стиль для `ApiClient(settings, transport=...)`. Handler видит real `httpx.Request`.""",
        "cheatsheet": """### О разделе — шпаргалка

Используй таблицу при code review: transport для контракта HTTP, mock для узкой ветки логики.""",
        "tiein": """### О разделе — связь с lab_fw

Логи retry уже в conftest — смотри WARNING при `pytest -v tests/mocks_lab`.""",
    }
    for k, v in mocks_ru.items():
        w(MOD / "mocks_lab" / "ru" / f"{k}.md", v)
    for lang in ("en", "pl"):
        for k, v in mocks_ru.items():
            w(MOD / "mocks_lab" / lang / f"{k}.md", v.replace("### О", "### About" if lang == "en" else "### O"))

    # fix en/pl mocks preamble
    w(MOD / "mocks_lab" / "en" / "00_preamble.md", "### About mocks_lab\n\nPattern catalog for mocks and MockTransport; root I2, [API README](../../../src/lab_fw/api/README.en.md).")
    w(MOD / "mocks_lab" / "pl" / "00_preamble.md", "### O mocks_lab\n\nKatalog wzorców mocków; I2, [API README](../../../src/lab_fw/api/README.pl.md).")


def main():
    write_l1()
    write_modules()
    print("Deep blocks written under tools/l1_deep_blocks and tools/module_deep_blocks")


if __name__ == "__main__":
    main()
