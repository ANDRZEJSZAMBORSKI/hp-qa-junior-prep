#!/usr/bin/env python3
"""Expand L1 subsections and module READMEs with textbook chapter blocks."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1_DIR = Path(__file__).resolve().parent / "l1_deep_blocks"
MOD_DIR = Path(__file__).resolve().parent / "module_deep_blocks"

L1_MARKER = "<!-- l1-deep:{n} -->"
MOD_MARKER = "<!-- mod-deep:{key} -->"


def _refresh_end_index(rest: str, marker: str) -> int:
    if "mod-deep:" in marker or "mod-preamble" in marker:
        m = re.search(r"\n## ", rest)
    elif "l1-deep:" in marker:
        m = re.search(r"\n(?=### \d+\.|\n## )", rest)
    else:
        m = re.search(r"\n(?=#### |\n### \d+\.|\n## )", rest)
    return m.start() if m else len(rest)


def insert_after_heading(content: str, heading: str, marker: str, block: str) -> str:
    if marker in content:
        start = content.find(marker)
        rest = content[start + len(marker) :]
        end = start + len(marker) + _refresh_end_index(rest, marker)
        return content[:start] + f"{marker}\n{block}\n" + content[end:].lstrip("\n")
    idx = content.find(heading)
    if idx == -1:
        raise ValueError(f"Missing heading: {heading!r}")
    line_end = content.find("\n", idx)
    return content[: line_end + 1] + f"\n{marker}\n{block}\n" + content[line_end + 1 :]


def load_l1(lang: str, n: int) -> str:
    return (L1_DIR / lang / f"{n:02d}.md").read_text(encoding="utf-8-sig").strip() + "\n"


def load_mod(lang: str, module: str, key: str) -> str:
    return (MOD_DIR / module / lang / f"{key}.md").read_text(encoding="utf-8-sig").strip() + "\n"


L1_HEADINGS = {
    "ru": [
        "### 1. Async communication",
        "### 2. Queue / event / message broker",
        "### 3. Retry vs timeout",
        "### 4. Timeout",
        "### 5. Idempotency",
        "### 6. Eventual consistency",
        "### 7. Logs vs metrics vs traces",
        "### 8. Correlation / Request / Trace ID",
        "### 9. Env vs build («locally green ≠ CI»)",
    ],
    "en": [
        "### 1. Async communication",
        "### 2. Queue / event / message broker",
        "### 3. Retry vs timeout",
        "### 4. Timeout",
        "### 5. Idempotency",
        "### 6. Eventual consistency",
        "### 7. Logs vs metrics vs traces",
        "### 8. Correlation / Request / Trace ID",
        "### 9. Env vs build (“locally green ≠ CI”)",
    ],
    "pl": [
        "### 1. Async communication",
        "### 2. Queue / event / message broker",
        "### 3. Retry vs timeout",
        "### 4. Timeout",
        "### 5. Idempotency",
        "### 6. Eventual consistency",
        "### 7. Logs vs metrics vs traces",
        "### 8. Correlation / Request / Trace ID",
        "### 9. Env vs build („locally green ≠ CI”)",
    ],
}

README = {"ru": ROOT / "README.md", "en": ROOT / "README.en.md", "pl": ROOT / "README.pl.md"}

MODULES = {
    "api": {
        "ru": ROOT / "src/lab_fw/api/README.md",
        "en": ROOT / "src/lab_fw/api/README.en.md",
        "pl": ROOT / "src/lab_fw/api/README.pl.md",
    },
    "reporting": {
        "ru": ROOT / "src/lab_fw/reporting/README.md",
        "en": ROOT / "src/lab_fw/reporting/README.en.md",
        "pl": ROOT / "src/lab_fw/reporting/README.pl.md",
    },
    "mocks_lab": {
        "ru": ROOT / "tests/mocks_lab/README.md",
        "en": ROOT / "tests/mocks_lab/README.en.md",
        "pl": ROOT / "tests/mocks_lab/README.pl.md",
    },
}

MODULE_HEADINGS: dict[str, dict[str, dict[str, str]]] = {
    "api": {
        "ru": {
            "preamble": "HTTP-клиент `ApiClient` и демо-слой auth.",
            "install": "## Установка",
            "settings": "## Settings / token",
            "bearer": "## Bearer",
            "oauth": "## Client credentials (mock-flow)",
            "schema": "## Schema (pydantic)",
            "negative": "## Negative / errors",
            "retry": "## Retry policy",
            "tests": "## Тесты",
        },
        "en": {
            "preamble": "HTTP client `ApiClient` and a demo auth layer.",
            "install": "## Install",
            "settings": "## Settings / token",
            "bearer": "## Bearer",
            "oauth": "## Client credentials (mock flow)",
            "schema": "## Schema (pydantic)",
            "negative": "## Negative / errors",
            "retry": "## Retry policy",
            "tests": "## Tests",
        },
        "pl": {
            "preamble": "Klient HTTP `ApiClient` i warstwa auth (demo).",
            "install": "## Instalacja",
            "settings": "## Settings / token",
            "bearer": "## Bearer",
            "oauth": "## Client credentials (mock-flow)",
            "schema": "## Schema (pydantic)",
            "negative": "## Negative / errors",
            "retry": "## Retry policy",
            "tests": "## Testy",
        },
    },
    "reporting": {
        "ru": {
            "preamble": "Слой отчёта фреймворка. Тесты и `ApiClient` вызывают этот API, а не `allure` напрямую.",
            "install": "## Установка",
            "api": "## API",
            "n1": "## Метаданные Allure (N1)",
            "run": "## Прогон с Allure",
            "n2": "## TestRail и Jira (N2)",
            "tests": "## Тесты слоя",
        },
        "en": {
            "preamble": "Framework reporting layer. Tests and `ApiClient` call this API instead of `allure` directly.",
            "install": "## Install",
            "api": "## API",
            "n1": "## Allure metadata (N1)",
            "run": "## Run with Allure",
            "n2": "## TestRail and Jira (N2)",
            "tests": "## Layer tests",
        },
        "pl": {
            "preamble": "Warstwa raportowania. Testy i `ApiClient` wołają ten API, nie `allure` bezpośrednio.",
            "install": "## Instalacja",
            "api": "## API",
            "n1": "## Metadane Allure (N1)",
            "run": "## Uruchomienie z Allure",
            "n2": "## TestRail i Jira (N2)",
            "tests": "## Testy warstwy",
        },
    },
    "mocks_lab": {
        "ru": {
            "preamble": "Демонстрирует подмену зависимостей на разных уровнях: объект/метод в Python и транспорт `httpx` у `ApiClient`.",
            "run": "## Как запускать",
            "structure": "## Структура",
            "pure": "## Часть I — чистые моки",
            "transport": "## Часть II — `httpx.MockTransport`",
            "cheatsheet": "## Когда что выбирать (шпаргалка)",
            "tiein": "## Связь с `lab_fw`",
        },
        "en": {
            "preamble": "Shows dependency substitution at two levels: Python mocks and `httpx` transport on `ApiClient`.",
            "run": "## How to run",
            "structure": "## Layout",
            "pure": "## Part I — pure mocks",
            "transport": "## Part II — `httpx.MockTransport`",
            "cheatsheet": "## When to use what (cheat sheet)",
            "tiein": "## Tie-in with `lab_fw`",
        },
        "pl": {
            "preamble": "Pokazuje podmianę zależności: mocki Pythona i transport `httpx` w `ApiClient`.",
            "run": "## Jak uruchamiać",
            "structure": "## Struktura",
            "pure": "## Część I — czyste mocki",
            "transport": "## Część II — `httpx.MockTransport`",
            "cheatsheet": "## Kiedy co wybrać (ściąga)",
            "tiein": "## Związek z `lab_fw`",
        },
    },
}


def apply_l1(lang: str) -> None:
    path = README[lang]
    text = path.read_text(encoding="utf-8")
    # remove duplicate one-liner under L1 chapter if present
    text = text.replace(
        "\n\nТермины и связь с реализацией в `lab_fw` (retry, timeout, `ApiError`, Compose/CI).\n\n### 1.",
        "\n\n### 1.",
        1,
    )
    text = re.sub(
        r"\n\nTerms and how they appear in `lab_fw`[^\n]+\n\n### 1\. Async",
        "\n\n### 1. Async",
        text,
        count=1,
    )
    text = re.sub(
        r"\n\nTerminy i powiązanie z `lab_fw`[^\n]+\n\n### 1\. Async",
        "\n\n### 1. Async",
        text,
        count=1,
    )
    for i, heading in enumerate(L1_HEADINGS[lang], start=1):
        block = load_l1(lang, i)
        text = insert_after_heading(text, heading, L1_MARKER.format(n=i), block)
    path.write_text(text, encoding="utf-8")
    print(f"L1 expanded: {path.name}")


def apply_module(module: str, lang: str) -> None:
    path = MODULES[module][lang]
    text = path.read_text(encoding="utf-8")
    heads = MODULE_HEADINGS[module][lang]
    pre = load_mod(lang, module, "00_preamble")
    old_pre = heads["preamble"]
    pre_marker = "<!-- mod-preamble -->"
    if pre_marker not in text:
        text = text.replace(old_pre, f"{pre_marker}\n\n{pre.strip()}\n\n{old_pre}", 1)
    else:
        start = text.find(pre_marker)
        rest = text[start + len(pre_marker) :]
        m = re.search(r"\n## ", rest)
        end = start + len(pre_marker) + (m.start() if m else len(rest))
        text = text[:start] + f"{pre_marker}\n\n{pre.strip()}\n\n" + text[end:].lstrip("\n")
    for key, heading in heads.items():
        if key == "preamble":
            continue
        block = load_mod(lang, module, key)
        text = insert_after_heading(text, heading, MOD_MARKER.format(key=f"{module}:{key}"), block)
    path.write_text(text, encoding="utf-8")
    print(f"Module {module} expanded: {path.relative_to(ROOT)}")


def main() -> None:
    for lang in ("ru", "en", "pl"):
        apply_l1(lang)
        for mod in MODULES:
            apply_module(mod, lang)
    print("All expansions applied.")


if __name__ == "__main__":
    main()
