#!/usr/bin/env python3
"""Insert textbook-style chapter blocks into README.md / README.en.md / README.pl.md."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCKS = Path(__file__).resolve().parent / "readme_blocks"

MARKER = "<!-- readme-chapter:{key} -->"

HEADINGS: dict[str, dict[str, str]] = {
    "quickstart": {
        "ru": "## Быстрый старт (локально)",
        "en": "## Quick start (local)",
        "pl": "## Szybki start (lokalnie)",
    },
    "structure": {
        "ru": "## Структура",
        "en": "## Layout",
        "pl": "## Struktura",
    },
    "env": {
        "ru": "## Переменные окружения",
        "en": "## Environment variables",
        "pl": "## Zmienne środowiskowe",
    },
    "markers": {
        "ru": "## Маркеры pytest",
        "en": "## Pytest markers",
        "pl": "## Markery pytest",
    },
    "docker": {
        "ru": "## Docker",
        "en": "## Docker",
        "pl": "## Docker",
    },
    "gha": {
        "ru": "## GitHub Actions",
        "en": "## GitHub Actions",
        "pl": "## GitHub Actions",
    },
    "i1": {
        "ru": "## Схема взаимодействия API (I1)",
        "en": "## API interaction diagram (I1)",
        "pl": "## Schemat interakcji API (I1)",
    },
    "l1": {
        "ru": "## Распределённые системы: теория и термины (L1)",
        "en": "## Distributed systems: theory and terms (L1)",
        "pl": "## Systemy rozproszone: teoria i terminy (L1)",
    },
    "l2": {
        "ru": "## L2 — очередь, retry, timeout, deadline, idempotency",
        "en": "## L2 — queue, retry, timeout, deadline, idempotency",
        "pl": "## L2 — kolejka, retry, timeout, deadline, idempotency",
    },
    "l3": {
        "ru": "## L3 — расследование сбоев (чек-лист)",
        "en": "## L3 — failure investigation checklist",
        "pl": "## L3 — badanie awarii (checklista)",
    },
    "m1": {
        "ru": "## M1 — параллельное выполнение и изоляция ресурсов",
        "en": "## M1 — parallel execution and resource isolation",
        "pl": "## M1 — równoległe uruchamianie i izolacja zasobów",
    },
    "m2": {
        "ru": "## M2 — удалённый браузер (Selenium Grid) и UI в Docker",
        "en": "## M2 — remote browser (Selenium Grid) and UI in Docker",
        "pl": "## M2 — zdalna przeglądarka (Selenium Grid) i UI w Dockerze",
    },
    "n1": {
        "ru": "## N1 — отчёты Allure",
        "en": "## N1 — Allure reporting",
        "pl": "## N1 — raporty Allure",
    },
    "n2": {
        "ru": "## N2 — Jira и TestRail",
        "en": "## N2 — Jira and TestRail",
        "pl": "## N2 — Jira i TestRail",
    },
    "n3": {
        "ru": "## N3 — тестирование на основе рисков (smoke и полная регрессия)",
        "en": "## N3 — risk-based testing (smoke and full regression)",
        "pl": "## N3 — testy oparte na ryzyku (smoke i pełna regresja)",
    },
    "allure_short": {
        "ru": "## Allure (кратко)",
        "en": "## Allure (short)",
        "pl": "## Allure (skrót)",
    },
    "modules": {
        "ru": "## Документация модулей",
        "en": "## Module docs",
        "pl": "## Dokumentacja modułów",
    },
    "extra": {
        "ru": "## Дополнительно",
        "en": "## Further reading",
        "pl": "## Dodatkowo",
    },
}

README_PATH = {
    "ru": ROOT / "README.md",
    "en": ROOT / "README.en.md",
    "pl": ROOT / "README.pl.md",
}

INTRO_OLD = {
    "ru": "Репозиторий автоматизации QA на Python: pytest-фреймворк `lab_fw`, API (httpx), UI (Playwright / Selenium), mocks, Allure, Docker, Docker Compose, GitHub Actions.",
    "en": "Python QA automation repository: `lab_fw` pytest framework, API (httpx), UI (Playwright / Selenium), mocks, Allure, Docker, Docker Compose, GitHub Actions.",
    "pl": "Repozytorium automatyzacji QA w Pythonie: framework pytest `lab_fw`, API (httpx), UI (Playwright / Selenium), mocki, Allure, Docker, Docker Compose, GitHub Actions.",
}


def load_block(key: str, lang: str) -> str:
    path = BLOCKS / lang / f"{key}.md"
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8").strip() + "\n"


def insert_after_heading(content: str, heading: str, key: str, block: str) -> str:
    marker = MARKER.format(key=key)
    if marker in content:
        # Do not replace until next ## — long chapter bodies live outside the block.
        return content
    idx = content.find(heading)
    if idx == -1:
        raise ValueError(f"Heading not found: {heading!r}")
    line_end = content.find("\n", idx)
    if line_end == -1:
        line_end = len(content)
    injection = f"\n{marker}\n{block}\n"
    return content[: line_end + 1] + injection + content[line_end + 1 :]


def apply_preamble(content: str, lang: str) -> str:
    marker = "<!-- readme-preamble -->"
    preamble = load_block("00_preamble", lang)
    if marker in content:
        start = content.find(marker)
        rest = content[start + len(marker) :]
        m = re.search(r"\n## ", rest)
        end = start + len(marker) + (m.start() if m else len(rest))
        return content[:start] + f"{marker}\n\n{preamble.strip()}\n\n" + content[end:].lstrip("\n")
    old = INTRO_OLD[lang]
    if old not in content:
        raise ValueError(f"Intro line missing for {lang}")
    return content.replace(old, f"{marker}\n\n{preamble.strip()}", 1)


def process_lang(lang: str) -> None:
    path = README_PATH[lang]
    text = path.read_text(encoding="utf-8")
    text = apply_preamble(text, lang)
    for key, headings in HEADINGS.items():
        block = load_block(key, lang)
        text = insert_after_heading(text, headings[lang], key, block)
    path.write_text(text, encoding="utf-8")
    print(f"Updated {path.name} ({lang}): {text.count(MARKER.split('{')[0])} chapter markers")


def main() -> None:
    for lang in ("ru", "en", "pl"):
        process_lang(lang)
    print("Done.")


if __name__ == "__main__":
    main()
