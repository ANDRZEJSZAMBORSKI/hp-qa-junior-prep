### O tym rozdziale

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
