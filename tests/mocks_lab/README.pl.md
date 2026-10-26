# Mocks lab

[RU](README.md) · [EN](README.en.md) · **PL**

Moduł: **czyste mocki** (`unittest.mock`, `patch`, spy, `monkeypatch`) oraz **`httpx.MockTransport`** na naszym `ApiClient` / `Settings` / `ApiError` / `retry_call` / logging / pytest.

Pokazuje podmianę zależności na dwóch poziomach: mocki obiektu/metody w Pythonie oraz transport `httpx` w `ApiClient`.

---

## Jak uruchamiać

<!-- mod-deep:mocks_lab:run -->
#### O sekcji — uruchomienie

Filtry `mocks_pure` / `mocks_httpx` dzielą część I i II bez ręcznego wypisywania plików.

## Struktura

<!-- mod-deep:mocks_lab:structure -->
#### O sekcji — struktura

Dwa pliki transportowe celowo powtarzają te same idee — porównaj fixture vs ręczne Settings.

## Część I — czyste mocki

<!-- mod-deep:mocks_lab:pure -->
#### O sekcji — czyste mocki

Patch „w złym miejscu” to częsty błąd juniora. Pytaj: podmieniamy **klienta**, **metodę** czy **transport**?

## Część II — `httpx.MockTransport`

<!-- mod-deep:mocks_lab:transport -->
#### O sekcji — MockTransport

Preferowany styl dla `ApiClient(settings, transport=...)`. Handler widzi prawdziwy `httpx.Request`.

## Kiedy co wybrać (ściąga)

<!-- mod-deep:mocks_lab:cheatsheet -->
#### O sekcji — ściąga

Używaj tabeli przy code review: transport dla kontraktu HTTP, mock dla wąskiej gałęzi logiki.

## Związek z `lab_fw`

<!-- mod-deep:mocks_lab:tiein -->
#### O sekcji — powiązanie z lab_fw

Logi retry są już w conftest — szukaj WARNING przy `pytest -v tests/mocks_lab`.

