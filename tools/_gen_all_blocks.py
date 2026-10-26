# One-off generator for readme_blocks/*.md — run: python tools/_gen_all_blocks.py
from pathlib import Path

OUT = Path(__file__).resolve().parent / "readme_blocks"

# fmt: off
BLOCKS = {
"quickstart": {
"ru": r'''### О разделе

Минимальный путь от пустой машины до «зелёного» прогона unit/API без браузера и без MockServer. Это тот же набор, что workflow **tests** на GitHub (без маркера `compose`).

### Пошагово

1. Клонируй репозиторий, перейди в корень.
2. Создай venv на **Python 3.11+** и активируй его.
3. `pip install -e ".[dev]"` — editable install пакета `lab-fw` и dev-зависимостей (pytest, xdist, allure, playwright, selenium, filelock).
4. Запусти быстрый suite (см. команду ниже). Ожидание: сотни passed, 0 failed; время — минуты на ноутбуке.

### Что означает фильтр маркеров

`-m "not ui and not selenium and not compose"` исключает тесты, которым нужен реальный браузер или контейнер `mock-api`. Так локально не нужны Docker и `playwright install` для первого успеха.

### UI (отдельный шаг)

Playwright и Selenium требуют браузер. Playwright: `playwright install chromium`. Selenium 4 на Windows часто тянет Chrome через Selenium Manager автоматически.

### Самопроверка

| Вопрос | Где ответ |
|--------|-----------|
| Пакет установлен editable? | `python -m pip show lab-fw` → Location внутри твоего `.venv` |
| xdist работает? | В выводе pytest есть `[gw0]` при `-n auto` |
| Почему не бегут compose-тесты? | Нет MockServer — см. раздел Docker |

### Типичные проблемы

- **`python` не 3.11** — переустанови venv с нужной версией.
- **Import errors** — активирован ли venv; выполнен ли `pip install -e ".[dev]"`.
- **Playwright без браузера** — не запускай `-m ui` до `playwright install`.
''',
"en": r'''### About this section

The shortest path from a clean machine to a green unit/API run without a browser or MockServer — the same slice as the GitHub **tests** workflow (no `compose` marker).

### Step by step

1. Clone the repo and `cd` into the root.
2. Create a **Python 3.11+** venv and activate it.
3. `pip install -e ".[dev]"` — editable `lab-fw` plus pytest, xdist, allure, playwright, selenium, filelock.
4. Run the fast suite (command below). Expect hundreds of passes; runtime is a few minutes on a laptop.

### Marker filter

`-m "not ui and not selenium and not compose"` skips tests that need a real browser or the `mock-api` container. You do not need Docker or `playwright install` for the first green run.

### UI (separate step)

Playwright and Selenium need a browser. For Playwright run `playwright install chromium`. Selenium 4 on Windows often resolves Chrome via Selenium Manager.

### Self-check

| Question | Where to look |
|----------|----------------|
| Editable install? | `python -m pip show lab-fw` → Location under your `.venv` |
| xdist active? | pytest output shows `[gw0]` with `-n auto` |
| Why no compose tests? | No MockServer — see Docker |

### Common issues

- **Wrong Python** — recreate the venv with 3.11+.
- **Import errors** — venv activated? `pip install -e ".[dev]"` done?
- **Playwright** — do not run `-m ui` before `playwright install`.
''',
"pl": r'''### O tym rozdziale

Najkrótsza ścieżka od czystej maszyny do zielonego przebiegu unit/API bez przeglądarki i MockServer — ten sam wycinek co workflow **tests** na GitHubie (bez markera `compose`).

### Krok po kroku

1. Sklonuj repo, wejdź do katalogu głównego.
2. Utwórz venv na **Pythonie 3.11+** i aktywuj.
3. `pip install -e ".[dev]"` — editable `lab-fw` oraz pytest, xdist, allure, playwright, selenium, filelock.
4. Uruchom szybki suite (polecenie poniżej). Oczekuj setek passed; kilka minut na laptopie.

### Filtr markerów

`-m "not ui and not selenium and not compose"` pomija testy wymagające prawdziwej przeglądarki lub kontenera `mock-api`. Do pierwszego sukcesu nie potrzebujesz Dockera ani `playwright install`.

### UI (osobno)

Playwright i Selenium wymagają przeglądarki. Playwright: `playwright install chromium`. Selenium 4 na Windows często sam pobiera Chrome (Selenium Manager).

### Samokontrola

| Pytanie | Gdzie sprawdzić |
|---------|-----------------|
| Editable install? | `python -m pip show lab-fw` |
| Działa xdist? | w output pytest jest `[gw0]` przy `-n auto` |
| Dlaczego brak compose? | brak MockServer — sekcja Docker |

### Typowe problemy

- **Zła wersja Pythona** — nowe venv 3.11+.
- **Import errors** — venv aktywne? `pip install -e ".[dev]"`?
- **Playwright** — nie uruchamiaj `-m ui` przed `playwright install`.
''',
},
"structure": {
"ru": r'''### О разделе

Карта репозитория: где лежит переиспользуемый код фреймворка, где сценарии pytest, как связаны Docker и CI.

### Дерево (основное)

| Путь | Содержимое |
|------|------------|
| `src/lab_fw/api/` | `ApiClient`, retry, auth, ошибки |
| `src/lab_fw/ui/` | Playwright / Selenium clients, page objects |
| `src/lab_fw/config/` | `Settings`, env, pydantic |
| `src/lab_fw/reporting/` | Allure decorators, steps, attachments |
| `src/lab_fw/pytest_plugin/` | hooks, markers integration |
| `src/distributed_lab/` | `Job`, `Worker`, `InMemoryQueue` (L2) |
| `tests/` | все pytest-модули |
| `tests/mocks_lab/` | чистые моки и MockTransport (I2) |
| `tests/distributed_lab/` | L2/L3 |
| `tests/parallel_lab/` | M1, xdist и файлы |
| `scripts/` | вспомогательные скрипты (TestRail upload) |
| `categories.json` | правила Allure Categories |
| `.github/workflows/` | **tests** и **CI** |

### Два слоя

- **`lab_fw`** — библиотека, которую импортируют тесты; её можно ставить editable и переиспользовать в других проектах.
- **`tests/`** — демонстрация паттернов; падение теста часто указывает на регрессию фреймворка или контракта.

### Самопроверка

Открой `pyproject.toml`: `[tool.setuptools.packages.find] where = ["src"]`. Убедись, что после install `import lab_fw` работает из корня репо.
''',
"en": r'''### About this section

A map of the repo: reusable framework code, pytest scenarios, and how Docker/CI tie in.

### Tree (main paths)

| Path | Contents |
|------|----------|
| `src/lab_fw/api/` | `ApiClient`, retry, auth, errors |
| `src/lab_fw/ui/` | Playwright / Selenium clients, pages |
| `src/lab_fw/config/` | `Settings`, env, pydantic |
| `src/lab_fw/reporting/` | Allure decorators, steps, attachments |
| `src/lab_fw/pytest_plugin/` | hooks, markers |
| `src/distributed_lab/` | `Job`, `Worker`, `InMemoryQueue` (L2) |
| `tests/` | all pytest modules |
| `tests/mocks_lab/` | pure mocks and MockTransport (I2) |
| `tests/distributed_lab/` | L2/L3 |
| `tests/parallel_lab/` | M1, xdist and files |
| `scripts/` | helpers (TestRail upload) |
| `categories.json` | Allure Categories rules |
| `.github/workflows/` | **tests** and **CI** |

### Two layers

- **`lab_fw`** — library imported by tests; editable install for reuse.
- **`tests/`** — pattern catalog; failures often signal framework or contract regressions.

### Self-check

In `pyproject.toml`, packages live under `src/`. After install, `import lab_fw` must work from the repo root.
''',
"pl": r'''### O tym rozdziale

Mapa repozytorium: kod frameworka, scenariusze pytest, Docker i CI.

### Drzewo (główne ścieżki)

| Path | Zawartość |
|------|-----------|
| `src/lab_fw/api/` | `ApiClient`, retry, auth, błędy |
| `src/lab_fw/ui/` | Playwright / Selenium, page objects |
| `src/lab_fw/config/` | `Settings`, env |
| `src/lab_fw/reporting/` | dekoratory Allure |
| `src/lab_fw/pytest_plugin/` | hooki, markery |
| `src/distributed_lab/` | `Job`, `Worker`, kolejka (L2) |
| `tests/mocks_lab/` | mocki (I2) |
| `tests/distributed_lab/` | L2/L3 |
| `tests/parallel_lab/` | M1 |
| `scripts/` | upload TestRail |
| `categories.json` | Allure Categories |
| `.github/workflows/` | **tests**, **CI** |

### Dwa poziomy

- **`lab_fw`** — biblioteka importowana przez testy.
- **`tests/`** — katalog wzorców i regresji.

### Samokontrola

Po `pip install -e ".[dev]"` polecenie `import lab_fw` z katalogu głównego musi działać.
''',
},
}
# fmt: on

def write_rest():
    """Generate remaining blocks with shared template helper."""
    templates = _remaining_templates()
    for key, langs in templates.items():
        for lang, text in langs.items():
            d = OUT / lang
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{key}.md").write_text(text.strip() + "\n", encoding="utf-8")


def _remaining_templates() -> dict:
    # Import large block set from companion - defined below in same file
    return {**BLOCKS, **_EXTRA}


_EXTRA = {}

def _add(key, ru, en, pl):
    _EXTRA[key] = {"ru": ru, "en": en, "pl": pl}


# --- env ---
_add("env",
"### О разделе\n\nКонфигурация через переменные окружения и `Settings`. Большинство API-тестов с MockTransport **не требуют** реального токена.\n\n### Приоритет\n\n1. Явный аргумент / fixture в тесте.\n2. Env (`LAB_FW_*`).\n3. Значения по умолчанию в коде (`example.com`, timeout 5s).\n\n### Практика\n\n- Локально можно не задавать `LAB_FW_API_TOKEN` — многие тесты пройдут.\n- В CI workflow **tests** токен **обязателен** (Secret) — пример расхождения env.\n- Для Compose API используй `http://mock-api:1080` в `Settings`, а не глобальный `LAB_FW_BASE_URL`.\n\n### Самопроверка\n\n```bash\npython -c \"from lab_fw.config import get_settings; s=get_settings(); print(s.base_url, s.timeout_s)\"\n```\n",
"### About this section\n\nConfiguration via environment variables and `Settings`. Most MockTransport API tests **do not** need a real token.\n\n### Precedence\n\n1. Explicit test/fixture values.\n2. Env (`LAB_FW_*`).\n3. Code defaults (`example.com`, 5s timeout).\n\n### Practice\n\n- Locally `LAB_FW_API_TOKEN` may be unset.\n- CI **tests** workflow requires the Secret token — typical env drift.\n- Compose API tests should pass `http://mock-api:1080` in `Settings`, not a global `LAB_FW_BASE_URL`.\n\n### Self-check\n\n```bash\npython -c \"from lab_fw.config import get_settings; s=get_settings(); print(s.base_url, s.timeout_s)\"\n```\n",
"### O tym rozdziale\n\nKonfiguracja przez env i `Settings`. Większość testów MockTransport **nie wymaga** prawdziwego tokenu.\n\n### Kolejność\n\n1. Wartość w teście/fixture.\n2. Env (`LAB_FW_*`).\n3. Domyślne w kodzie.\n\n### Praktyka\n\n- Lokalnie token może być pusty.\n- W CI workflow **tests** token ze Secrets jest wymagany.\n- Testy Compose: `http://mock-api:1080` w `Settings`.\n\n### Samokontrola\n\n```bash\npython -c \"from lab_fw.config import get_settings; s=get_settings(); print(s.base_url, s.timeout_s)\"\n```\n",
)

_add("markers",
"### О разделе\n\nМаркеры — «рубильники» для выбора подмножества тестов и для CI. Они **не** поднимают инфраструктуру сами.\n\n### Как CI использует маркеры\n\n| Workflow | Фильтр | Эффект |\n|----------|--------|--------|\n| **tests** | `not ui`, `not selenium`, `not compose` | быстрый runner без Docker |\n| **CI** / Docker CMD | часто без `not compose` | compose-тесты при живом `mock-api` |\n| Compose services | см. M2 | `serial` vs параллельный UI |\n\n### Учебный смысл\n\n- `distributed_lab` — L2/L3, без Docker.\n- `parallel_lab` — M1, xdist и файлы.\n- `reporting` — декораторы Allure.\n\n### Самопроверка\n\n`pytest --markers | findstr /i compose` (Windows) или `pytest --markers | rg compose` — описание из `pyproject.toml`.\n",
"### About this section\n\nMarkers select test subsets and drive CI. They **do not** start infrastructure.\n\n### CI usage\n\n| Workflow | Filter | Effect |\n|----------|--------|--------|\n| **tests** | `not ui`, `not selenium`, `not compose` | fast runner, no Docker |\n| **CI** / Docker CMD | often includes compose | needs `mock-api` |\n| Compose services | see M2 | `serial` vs parallel UI |\n\n### Learning tracks\n\n- `distributed_lab` — L2/L3.\n- `parallel_lab` — M1.\n- `reporting` — Allure decorators.\n\n### Self-check\n\nRun `pytest --markers` and confirm `compose`, `serial`, `distributed_lab` descriptions.\n",
"### O tym rozdziale\n\nMarkery wybierają podzbiory testów i sterują CI. **Nie** uruchamiają infrastruktury.\n\n### CI\n\n| Workflow | Filtr | Efekt |\n|----------|-------|--------|\n| **tests** | bez ui/selenium/compose | szybki runner |\n| **CI** | często z compose | wymaga `mock-api` |\n\n### Ścieżki\n\n- `distributed_lab` — L2/L3.\n- `parallel_lab` — M1.\n- `reporting` — Allure.\n\n### Samokontrola\n\n`pytest --markers` — opisy w `pyproject.toml`.\n",
)

_add("docker",
"### О разделе\n\nDocker воспроизводит CI локально: один образ `tests`, сервис MockServer, опционально Grid и Playwright.\n\n### Mental model\n\n1. **Образ `ci`** — pytest в Linux-контейнере.\n2. **Compose network** — `tests` резолвит `mock-api` по DNS.\n3. **Profiles** — UI не стартует по умолчанию (экономия ресурсов).\n\n### Когда нужен `DOCKER_TARGET=local`\n\nКорпоративный MITM (Avast и т.п.): target **local** кладёт CA в образ. Файл `avast-root.crt` только на твоей машине.\n\n### Самопроверка\n\n```bash\ndocker compose up --build --abort-on-container-exit tests\n```\n\nExit code 0 и лог pytest с passed compose-тестами.\n\n### Типичные ошибки\n\n- Запуск compose-тестов на голом `pytest` без `mock-api`.\n- Путаница CMD образа (включает compose) vs workflow **tests** (исключает).\n",
"### About this section\n\nDocker reproduces CI locally: a `tests` image, MockServer, optional Grid/Playwright.\n\n### Mental model\n\n1. **`ci` image** — pytest on Linux.\n2. **Compose network** — `tests` resolves `mock-api`.\n3. **Profiles** — UI is opt-in.\n\n### `DOCKER_TARGET=local`\n\nCorporate MITM: **local** target adds your CA; `avast-root.crt` stays untracked.\n\n### Self-check\n\n```bash\ndocker compose up --build --abort-on-container-exit tests\n```\n\n### Common mistakes\n\n- Running `compose` tests without `mock-api`.\n- Confusing image CMD (runs compose) with **tests** workflow (excludes compose).\n",
"### O tym rozdziale\n\nDocker odtwarza CI lokalnie: obraz `tests`, MockServer, opcjonalnie Grid/Playwright.\n\n### Model\n\n1. Obraz **ci** — pytest w Linuxie.\n2. Sieć Compose — `mock-api` po DNS.\n3. Profile — UI opcjonalnie.\n\n### `DOCKER_TARGET=local`\n\nMITM — target **local** + `avast-root.crt` lokalnie.\n\n### Samokontrola\n\n`docker compose up --build --abort-on-container-exit tests`\n\n### Błędy\n\n- Compose bez `mock-api`.\n- Mylenie CMD obrazu z workflow **tests**.\n",
)

_add("gha",
"### О разделе\n\nДва pipeline дополняют друг друга: быстрая обратная связь на runner и полный интеграционный прогон в Docker.\n\n### tests.yml\n\n- Установка зависимостей на ubuntu runner.\n- pytest с xdist, **без** ui/selenium/compose.\n- Artifact `allure-results` — частичный срез.\n\n### ci.yml\n\n- Полный Compose: API → down → Selenium (parallel + serial) → Playwright (parallel + serial).\n- Один aggregated `allure-results` после всех стадий.\n\n### Как учиться по Actions\n\n1. Открой упавший job → step log.\n2. Скачай artifact Allure.\n3. Сравни команду pytest с локальной из README.\n\n### Самопроверка\n\nFork + push → зелёный **tests** на каждом PR; **CI** длиннее, но даёт полную картину.\n",
"### About this section\n\nTwo pipelines: fast feedback on the runner and full integration in Docker.\n\n### tests.yml\n\n- ubuntu runner, xdist pytest, **no** ui/selenium/compose.\n- Partial `allure-results` artifact.\n\n### ci.yml\n\n- Full Compose chain including Selenium and Playwright stages.\n- Combined `allure-results`.\n\n### Learning from Actions\n\n1. Failed job → step log.\n2. Download Allure artifact.\n3. Compare pytest command with local README.\n\n### Self-check\n\nGreen **tests** on each push; **CI** is slower but complete.\n",
"### O tym rozdziale\n\nDwa pipeline: szybki runner i pełna integracja w Dockerze.\n\n### tests.yml\n\n- pytest bez ui/selenium/compose, artifact Allure (wycinek).\n\n### ci.yml\n\n- Pełny łańcuch Compose + Selenium + Playwright.\n\n### Nauka\n\nLogi joba → artifact → porównaj polecenie pytest z README.\n",
)

_add("i1",
"### О разделе (I1–I4)\n\nБлок **Integration / API**: как тестировать HTTP-клиент без продакшена и когда выносить мок в отдельный контейнер.\n\n| Подраздел | Тема |\n|-----------|------|\n| **I1** | Два режима: MockTransport vs MockServer |\n| **I2** | Стратегия моков, `tests/mocks_lab/` |\n| **I3** | 401, timeout, `ApiError` |\n| **I4** | Карта логов и CI |\n\n### Ключевые файлы\n\n- `src/lab_fw/api/client.py` — `ApiClient`, transport DI.\n- `tests/test_api_client.py` — MockTransport примеры + Allure (N2).\n- `tests/test_compose_api.py` — MockServer контракт.\n\n### Упражнение\n\n1. `pytest tests/mocks_lab -q` — in-process.\n2. `docker compose up … tests` — сеть между контейнерами.\n3. Сравни время и сложность отладки.\n\n### Контрольные вопросы\n\n- Почему `compose` не поднимает MockServer?\n- Чем HTTP 401 отличается от `ReadTimeout` в assertions?\n",
"### About this section (I1–I4)\n\n**Integration / API**: testing the HTTP client without production and when to use a container mock.\n\n| Part | Topic |\n|------|--------|\n| **I1** | MockTransport vs MockServer |\n| **I2** | Mock strategy, `tests/mocks_lab/` |\n| **I3** | 401, timeout, `ApiError` |\n| **I4** | Logs and CI map |\n\n### Key files\n\n- `src/lab_fw/api/client.py`\n- `tests/test_api_client.py`\n- `tests/test_compose_api.py`\n\n### Exercise\n\n1. `pytest tests/mocks_lab -q`\n2. `docker compose up … tests`\n3. Compare debug experience.\n\n### Review questions\n\n- Why doesn't `compose` start MockServer?\n- HTTP 401 vs `ReadTimeout` in tests?\n",
"### O tym rozdziale (I1–I4)\n\n**Integracja / API**: test klienta HTTP bez produkcji i kiedy mock w kontenerze.\n\n| Część | Temat |\n|-------|--------|\n| **I1** | MockTransport vs MockServer |\n| **I2** | Strategia mocków |\n| **I3** | 401, timeout |\n| **I4** | Logi i CI |\n\n### Pliki\n\n- `src/lab_fw/api/client.py`\n- `tests/test_compose_api.py`\n\n### Ćwiczenie\n\n`pytest tests/mocks_lab -q` vs `docker compose up … tests`.\n",
)

_add("l1",
"### О разделе\n\n**L1** — концептуальный фундамент для L2/L3: термины, которые встречаются в собеседованиях и в продакшен-логах.\n\n### Как учить\n\n1. Прочитай пункт 1–9 последовательно.\n2. После каждого найди отсылку в `lab_fw` (retry, timeout, `ApiError`).\n3. Перейди к L2 и посмотри, как абстракции стали кодом.\n\n### Связь с QA\n\nКолонка **QA** в таблицах — что проверять в тестах и в расследовании, а не только определения.\n\n### Самопроверка\n\nОбъясни своими словами: retry ≠ timeout; idempotency ≠ «тот же JSON»; eventual consistency ≠ «sleep 5 секунд».\n",
"### About this section\n\n**L1** — conceptual base for L2/L3: terms you will see in interviews and production logs.\n\n### Study path\n\n1. Read sections 1–9 in order.\n2. Map each term to `lab_fw` (retry, timeout, `ApiError`).\n3. Continue to L2 for executable models.\n\n### Self-check\n\nExplain: retry ≠ timeout; idempotency ≠ identical JSON; eventual consistency ≠ blind sleep.\n",
"### O tym rozdziale\n\n**L1** — fundament pod L2/L3: terminy z logów produkcyjnych i rozmów kwalifikacyjnych.\n\n### Nauka\n\nCzytaj 1–9, mapuj na `lab_fw`, potem L2.\n\n### Samokontrola\n\nretry ≠ timeout; idempotency ≠ ten sam JSON.\n",
)

_add("l2",
"### О разделе\n\n**L2** — минимальный «микросервисный» контур в одном процессе: очередь → worker → HTTP с политикой retry и лимитами времени.\n\n### Архитектура\n\n```text\nJob → InMemoryQueue → Worker.run_once → retry_call → ApiClient → HTTP (mock или test server)\n```\n\n### Чему учит код\n\n- Разные правила retry для GET и POST.\n- Три уровня времени: request timeout, job deadline, worker deadline.\n- Заголовок `Idempotency-Key` без мутации модели job.\n\n### Практика\n\nПрогоняй модули по отдельности (см. команды ниже), читай traceback при искусственных 503.\n\n### Самопроверка\n\nPOST с timeout не должен давать 3 попытки. GET 503→200 — три попытки, два WARNING в логах retry.\n",
"### About this section\n\n**L2** — queue → worker → HTTP with retry policy and time budgets.\n\n### Architecture\n\n```text\nJob → InMemoryQueue → Worker → retry_call → ApiClient\n```\n\n### Learning goals\n\n- GET vs POST retry rules.\n- Timeout vs job/worker deadlines.\n- `Idempotency-Key` on the wire.\n\n### Self-check\n\nPOST timeout → one attempt; GET 503→200 → three attempts.\n",
"### O tym rozdziale\n\n**L2** — kolejka → worker → HTTP z retry i limitami czasu.\n\n### Architektura\n\nJob → kolejka → Worker → ApiClient.\n\n### Samokontrola\n\nPOST — jedna próba przy timeout; GET retry przy 503.\n",
)

_add("l3",
"### О разделе\n\n**L3** — методика расследования: не гадать, а проходить фиксированный чек-лист **Env → Build → Logs → Metrics → Trace**.\n\n### Отличие от I4\n\n- **I4** — *где* лежат артеfacts (pytest, compose logs, Actions).\n- **L3** — *в каком порядке* смотреть сигналы и как фиксировать выводы (counters, caplog).\n\n### Практика в репо\n\n`tests/distributed_lab/test_l3_investigation.py` — retry с MockTransport, перехват WARNING через `caplog`.\n\n### Самопроверка\n\nВоспроизведи сценарий «503 три раза» и выпиши три счётчика из теста. Найди в коде grep по `X-Request-ID`.\n",
"### About this section\n\n**L3** — investigation checklist: **Env → Build → Logs → Metrics → Trace**.\n\n### I4 vs L3\n\n- **I4** — where artifacts live.\n- **L3** — order of analysis and caplog/counters practice.\n\n### Practice\n\n`tests/distributed_lab/test_l3_investigation.py`.\n\n### Self-check\n\nReplay triple-503 retry and record manual counters from the test.\n",
"### O tym rozdziale\n\n**L3** — checklista **Env → Build → Logs → Metrics → Trace**.\n\n### I4 vs L3\n\nI4 — gdzie szukać; L3 — kolejność analizy.\n\n### Praktyka\n\n`test_l3_investigation.py`.\n",
)

_add("m1",
"### О разделе\n\n**M1** — параллельный pytest (`pytest-xdist`): ускорение и **риски** общих ресурсов.\n\n### Главная идея\n\nПараллелизм безопасен только для **независимых** тестов. Общий MockServer, файл или браузер требуют стратегии: `xdist_group` + `--dist loadgroup`, отдельные файлы, `FileLock`, или `@serial`.\n\n### Где смотреть код\n\n- `tests/conftest.py` — `pytest_collection_modifyitems`, `tryfirst=True`.\n- `tests/test_compose_api.py` — `reset_mockserver` (не замена группировке!).\n- `tests/parallel_lab/test_parallel_resources.py` — файлы и lock.\n\n### Самопроверка\n\nВ логе compose + loadgroup видишь `@mockserver` и один worker для всех compose-тестов.\n",
"### About this section\n\n**M1** — parallel pytest and shared resource risks.\n\n### Core idea\n\nParallelism is safe for **independent** tests only. Shared MockServer/files/browser need `xdist_group`, `loadgroup`, separate files, `FileLock`, or `@serial`.\n\n### Code\n\n- `tests/conftest.py`\n- `tests/parallel_lab/`\n\n### Self-check\n\nCompose run shows `@mockserver` suffix and one worker for the group.\n",
"### O tym rozdziale\n\n**M1** — pytest-xdist i ryzyko współdzielonych zasobów.\n\n### Idea\n\nRównoległość dla testów niezależnych; MockServer/pliki — `loadgroup` lub `@serial`.\n\n### Kod\n\n`tests/conftest.py`, `tests/parallel_lab/`.\n",
)

_add("m2",
"### О разделе\n\n**M2** — UI-тесты как инфраструктура: браузер в Grid, runner pytest отдельно, два режима — parallel и **serial** (module state).\n\n### Playwright vs Selenium\n\n- **Playwright** в CI — образ `playwright` target (браузеры внутри).\n- **Selenium** — контейнер Grid, `SELENIUM_REMOTE_URL`.\n\n### noVNC\n\nПорт **7900** — визуальная отладка Grid локально.\n\n### Самопроверка\n\nModule-scoped login chains только с `-m serial` без `-n`. Параллельный UI — `-n 2` и достаточно сессий Grid.\n",
"### About this section\n\n**M2** — UI infrastructure: Grid browser, separate pytest runner, parallel vs **serial** module state.\n\n### Stacks\n\nPlaywright Docker target vs Selenium Grid + `SELENIUM_REMOTE_URL`.\n\n### Self-check\n\nModule login chains under `serial` only; parallel UI needs enough Grid sessions.\n",
"### O tym rozdziale\n\n**M2** — UI: Grid, runner pytest, parallel vs **serial**.\n\n### Samokontrola\n\nŁańcuchy module-scoped tylko w `serial`.\n",
)

_add("n1",
"### О разделе\n\n**N1** — Allure как аналитический отчёт: метаданные, категории падений, окружение прогона, шаги через `lab_fw.reporting`.\n\n### Поток данных\n\n```text\npytest --alluredir → conftest (categories + environment) → allure-results/ → CI artifact → allure serve\n```\n\n### Важно\n\n- xdist workers не пишут environment — только master process.\n- `categories.json` статический; env динамический.\n\n### Самопроверка\n\nОткрой Behaviors, Categories, Environment после локального `allure serve`.\n",
"### About this section\n\n**N1** — Allure for analysis: metadata, failure categories, environment, framework steps.\n\n### Data flow\n\npytest → conftest → `allure-results/` → CI artifact.\n\n### Notes\n\nMaster process writes environment; workers do not.\n\n### Self-check\n\nInspect Behaviors, Categories, Environment in Allure UI.\n",
"### O tym rozdziale\n\n**N1** — Allure: metadane, kategorie, environment, kroki frameworka.\n\n### Samokontrola\n\nBehaviors, Categories, Environment w UI.\n",
)

_add("n2",
"### О разделе\n\n**N2** — traceability: pytest ↔ TestRail ↔ Jira ↔ Allure. Два **независимых** канала (ссылки vs upload run).\n\n### Настройка trial\n\n1. Создай case C1/C2, поле References с node id pytest.\n2. Добавь `@testcase` / `@issue` на тесты.\n3. JUnit + trcli для run (канал B).\n\n### Безопасность\n\n`.env` с API key TestRail — только локально, в `.gitignore`.\n\n### Самопроверка\n\nLinks в Allure; в TestRail run — `test_id` = `C1`, не `1`; фильтр Assigned To снят.\n",
"### About this section\n\n**N2** — traceability across pytest, TestRail, Jira, Allure. Two **independent** channels (links vs run upload).\n\n### Trial setup\n\nCases, References, decorators, JUnit + trcli.\n\n### Security\n\nTestRail keys in local `.env` only.\n\n### Self-check\n\nAllure Links; TestRail `test_id` is `C1`; clear Assigned To filter.\n",
"### O tym rozdziale\n\n**N2** — traceability: pytest, TestRail, Jira, Allure; dwa kanały.\n\n### Samokontrola\n\nLinks w Allure; `test_id` = `C1`; filtr Assigned To.\n",
)

_add("allure_short",
"### О разделе\n\nКраткая шпаргалка команд Allure. Полная глава — [N1](#n1--отчёты-allure).\n\n### Когда использовать\n\n- Локальная отладка упавшего теста с attachments.\n- Просмотр artifact из GitHub Actions без полного CI локально.\n",
"### About this section\n\nQuick Allure commands. Full chapter: [N1](#n1--allure-reporting).\n",
"### O tym rozdziale\n\nSkrót poleceń Allure. Pełny rozdział: [N1](#n1--raporty-allure).\n",
)

_add("modules",
"### О разделе\n\nУглубление по подсистемам `lab_fw` и pytest. Корневой README — карта; модульные README — API контрактов, UI стеки, reporting decorators.\n\n### Рекомендуемый порядок\n\n1. [API](src/lab_fw/api/README.md) — клиент и ошибки.\n2. [Mocks lab](tests/mocks_lab/README.md) — швы подмены.\n3. [Reporting](src/lab_fw/reporting/README.md) — Allure слой.\n4. [UI](src/lab_fw/ui/README.md) — Playwright/Selenium.\n5. [Pytest plugin](src/lab_fw/pytest_plugin/README.md) — hooks.\n6. [README_PYTEST](tests/README_PYTEST.md) — изоляция и hygiene тестов.\n",
"### About this section\n\nDeep dives per subsystem. Start with API → mocks → reporting → UI → pytest plugin → README_PYTEST.\n",
"### O tym rozdziale\n\nSzczegóły modułów: API → mocks → reporting → UI → plugin → README_PYTEST.\n",
)

_add("extra",
"### О разделе\n\nВнешний тематический план навыков (отдельный файл), не часть runtime репозитория.\n\nИспользуй [PLAN_MID_HP.md](PLAN_MID_HP.md) как список тем для расширения практики поверх этого README.\n",
"### About this section\n\nExternal skill roadmap file — not required to run tests.\n\nSee [PLAN_MID_HP.md](PLAN_MID_HP.md) for extended topics beyond this README.\n",
"### O tym rozdziale\n\nZewnętrzny plan rozwoju — [PLAN_MID_HP.md](PLAN_MID_HP.md).\n",
)


def main():
    for key, langs in BLOCKS.items():
        for lang, text in langs.items():
            d = OUT / lang
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{key}.md").write_text(text.strip() + "\n", encoding="utf-8")
    write_rest()
    print("Wrote blocks to", OUT)


if __name__ == "__main__":
    main()
