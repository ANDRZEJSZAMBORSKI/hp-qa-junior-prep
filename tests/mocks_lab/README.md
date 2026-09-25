# Mocks lab

**RU** · [EN](README.en.md) · [PL](README.pl.md)

Учебный модуль: **чистые моки** (`unittest.mock`, `patch`, spy, `monkeypatch`) и **`httpx.MockTransport`** на нашем `ApiClient` / `Settings` / `ApiError` / `retry_call` / logging / pytest.

Цель — не «зелёный pytest ради галочки», а уметь объяснить на собесе: *что подменяем, на каком шве, и зачем*.

---

## Как запускать

Из корня `hp-qa-junior-prep` (venv активен):

```bash
# вся лаба
pytest -v tests/mocks_lab

# только чистые моки
pytest -v -m mocks_pure tests/mocks_lab

# только MockTransport
pytest -v -m mocks_httpx tests/mocks_lab

# всё помеченное mocks
pytest -v -m mocks tests/mocks_lab

# smoke-кейсы из лабы (stub / spy / monkeypatch)
pytest -v -m smoke tests/mocks_lab
```

Ожидай: логи `INFO [lab_fw.api] …`, при retry — `WARNING [lab_fw.core.retry] …`, в конце все тесты **passed**.  
Полный прогон репо: `pytest -q` (лаба + остальные тесты `lab_fw`).

---

## Структура

| Файл | Что внутри |
|------|------------|
| `test_unittest_mock_basics.py` | `Mock`: `return_value`, `side_effect`, `call_count`, `call_args_list` |
| `test_mock_patch_api_client.py` | `patch.object` / `patch(httpx.Client)` / `MagicMock` / `ConnectError` → `ApiError` |
| `test_mock_side_effect_and_calls.py` | `side_effect` + свой `@retry` и `retry_call` |
| `test_mock_vs_spy.py` | stub vs `Mock(wraps=…)` vs `monkeypatch.setattr` |
| `test_mock_transport_basics.py` | `MockTransport`: Settings **вручную** в тесте |
| `test_mock_transport_basics_02.py` | то же по смыслу, но `settings` из **fixture** (`conftest`) |

Два transport-файла и частично похожие кейсы **намеренны**: сравнить стили (ручной `Settings` vs fixture; один большой тест vs `@parametrize`).

Маркеры (`mocks`, `mocks_pure`, `mocks_httpx`, `smoke`) стоят там, где удобно для фильтра — это не единый «продуктовый» набор правил.

---

## Часть I — чистые моки

Подменяем **объект или метод** в Python:

- `Mock` / `MagicMock` — нет реального HTTP;
- `patch` / `patch.object` — временно подменить `request` или `httpx.Client`;
- `wraps=` — spy: реальная функция + история вызовов;
- `monkeypatch` — pytest-способ подменить атрибут класса/модуля на время теста.

Плюсы: быстро, точечно, удобно для unit.  
Минусы: легко «промахнуться швом» (патч не там); слабо видно реальный `httpx.Request` (path/params/headers/body).

---

## Часть II — `httpx.MockTransport`

Подменяем **транспорт** у настоящего `httpx.Client` внутри `ApiClient`:

```text
ApiClient → httpx.Client(transport=MockTransport(handler)) → handler(request) → Response | raise
```

Handler видит настоящий `httpx.Request` (method, path, params, headers) и может:

- вернуть JSON / text / нужный status;
- кинуть `ConnectError` / `ReadTimeout` → наш клиент поднимает `ApiError` (`__cause__` сохраняется);
- держать состояние (retry: 2 фейла → успех).

Плюсы: ближе к реальному HTTP-стеку без сети; DI через `transport=` чище, чем вечный `patch`.  
Минусы: чуть больше кода в handler; это всё ещё не live API.

---

## Когда что выбирать (шпаргалка)

| Задача | Обычно |
|--------|--------|
| Проверить свой retry / ветку без HTTP | `Mock` + `side_effect` |
| Подменить один метод уже созданного клиента | `patch.object` |
| Не создавать реальный `httpx.Client` | `patch("…httpx.Client")` |
| Убедиться, что ушёл нужный path/params/header | `MockTransport` + assert на `request` |
| Ошибка сети / timeout через клиент | `MockTransport` raise **или** `patch` + `side_effect` |
| Интеграция `ApiClient` + `retry_call` | `MockTransport` со счётчиком attempts |

На HP mid: **MockTransport / DI transport** — основной стиль для API-клиента; чистые моки — для изоляции хелперов и узких unit-тестов.

---

## Связь с `lab_fw`

- `ApiClient(settings, transport=…)` — точка расширения.
- `ApiError` оборачивает `httpx.HTTPError`.
- `retry_call` / учебный `@retry` — поверх вызовов клиента.
- Логирование уже поднимается в корневом `tests/conftest.py` (`pytest_configure` → `setup_logging`).
