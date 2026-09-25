# Mocks lab

[RU](README.md) · [EN](README.en.md) · **PL**

Moduł szkoleniowy: **czyste mocki** (`unittest.mock`, `patch`, spy, `monkeypatch`) oraz **`httpx.MockTransport`** na naszym `ApiClient` / `Settings` / `ApiError` / `retry_call` / logging / pytest.

Cel — nie „zielony pytest dla odznaki”, tylko umiejętność wyjaśnienia na rozmowie: *co podmieniamy, na którym szwie i po co*.

---

## Jak uruchamiać

Z katalogu głównego `hp-qa-junior-prep` (aktywne venv):

```bash
# cała laborka
pytest -v tests/mocks_lab

# tylko czyste mocki
pytest -v -m mocks_pure tests/mocks_lab

# tylko MockTransport
pytest -v -m mocks_httpx tests/mocks_lab

# wszystko oznaczone mocks
pytest -v -m mocks tests/mocks_lab

# smoke z laborki (stub / spy / monkeypatch)
pytest -v -m smoke tests/mocks_lab
```

Oczekuj: logi `INFO [lab_fw.api] …`; przy retry — `WARNING [lab_fw.core.retry] …`; na końcu wszystkie testy **passed**.  
Pełny przebieg repo: `pytest -q` (laborka + pozostałe testy `lab_fw`).

---

## Struktura

| Plik | Zawartość |
|------|-----------|
| `test_unittest_mock_basics.py` | `Mock`: `return_value`, `side_effect`, `call_count`, `call_args_list` |
| `test_mock_patch_api_client.py` | `patch.object` / `patch(httpx.Client)` / `MagicMock` / `ConnectError` → `ApiError` |
| `test_mock_side_effect_and_calls.py` | `side_effect` + własny `@retry` i `retry_call` |
| `test_mock_vs_spy.py` | stub vs `Mock(wraps=…)` vs `monkeypatch.setattr` |
| `test_mock_transport_basics.py` | `MockTransport`: `Settings` budowane **ręcznie** w teście |
| `test_mock_transport_basics_02.py` | te same idee, ale `settings` z **fixture** (`conftest`) |

Dwa pliki transport i częściowo podobne przypadki są **celowe**: porównanie stylów (ręczny `Settings` vs fixture; jeden duży test vs `@parametrize`).

Markery (`mocks`, `mocks_pure`, `mocks_httpx`, `smoke`) są tam, gdzie pomagają filtrować — to nie jednolita „produktowa” polityka.

---

## Część I — czyste mocki

Podmieniamy **obiekt lub metodę** w Pythonie:

- `Mock` / `MagicMock` — bez prawdziwego HTTP;
- `patch` / `patch.object` — tymczasowa podmiana `request` lub `httpx.Client`;
- `wraps=` — spy: prawdziwa funkcja + historia wywołań;
- `monkeypatch` — sposób pytest na podmianę atrybutu klasy/modułu na czas testu.

Zalety: szybko, precyzyjnie, dobre do unitów.  
Wady: łatwo trafić w zły szew (zły patch); słaba widoczność prawdziwego `httpx.Request` (path/params/headers/body).

---

## Część II — `httpx.MockTransport`

Podmieniamy **transport** prawdziwego `httpx.Client` wewnątrz `ApiClient`:

```text
ApiClient → httpx.Client(transport=MockTransport(handler)) → handler(request) → Response | raise
```

Handler widzi prawdziwy `httpx.Request` (method, path, params, headers) i może:

- zwrócić JSON / text / wybrany status;
- rzucić `ConnectError` / `ReadTimeout` → nasz klient podnosi `ApiError` (`__cause__` zachowane);
- trzymać stan (retry: 2 błędy → sukces).

Zalety: bliżej prawdziwego stosu HTTP bez sieci; DI przez `transport=` jest czystsze niż wieczny `patch`.  
Wady: trochę więcej kodu w handlerze; to nadal nie live API.

---

## Kiedy co wybrać (ściąga)

| Zadanie | Zwykle |
|---------|--------|
| Sprawdzić własny retry / gałąź bez HTTP | `Mock` + `side_effect` |
| Podmienić jedną metodę już utworzonego klienta | `patch.object` |
| Nie tworzyć prawdziwego `httpx.Client` | `patch("…httpx.Client")` |
| Upewnić się, że poszedł właściwy path/params/header | `MockTransport` + assert na `request` |
| Błąd sieci / timeout przez klienta | `MockTransport` raise **lub** `patch` + `side_effect` |
| Integracja `ApiClient` + `retry_call` | `MockTransport` z licznikiem attempts |

Na HP mid: **MockTransport / DI transport** — główny styl dla klienta API; czyste mocki — do izolacji helperów i wąskich unit-testów.

---

## Związek z `lab_fw`

- `ApiClient(settings, transport=…)` — punkt rozszerzenia.
- `ApiError` owija `httpx.HTTPError`.
- `retry_call` / szkoleniowy `@retry` — wokół wywołań klienta.
- Logowanie jest już uruchamiane w rootowym `tests/conftest.py` (`pytest_configure` → `setup_logging`).
