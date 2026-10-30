The **hp-qa-junior-prep** repository is a hands-on Python QA automation project. It bundles a reusable package **`lab_fw`** (HTTP client, UI layer, configuration, reporting, pytest plugin), a **pytest** suite, **Docker / Compose**, **GitHub Actions**, and **Allure** reporting. Typical runs **do not** call a production API: contracts are simulated with **MockTransport** and **MockServer** so you can practice isolation, integration, and troubleshooting without external dependencies.

This document is both a **runbook** (commands, env vars, CI) and a **textbook** (concepts, code mapping, common failures). Languages: [RU](README.md) · **EN** (this file) · [PL](README.pl.md).

### Audience

- QA / SDET engineers running the framework locally and in CI.
- Developers who need a clear picture of mocks, parallel pytest, and traceability (TestRail / Jira).

### Outcomes

- Choose the right test level: in-process mock vs container MockServer vs UI on Grid/Docker.
- Understand retry, timeout, deadline, and idempotency via `ApiClient` and `Worker`.
- Investigate failures using env → build → logs → metrics → trace.
- Use Allure and optionally link runs to TestRail and Jira.
- Apply **HTTP retry** policy (GET vs POST), **anti-flaky** hygiene, and **quarantine** without weakening CI.
- Tell **smoke**, **CI filter**, and **full collection** apart; read **tests** vs **CI** workflows.
- Run an **AI-assisted** loop: diff → pytest → Actions, no blind merge.

### Requirements

| Component | Version / notes |
|-----------|-----------------|
| Python | **≥ 3.11** (`pyproject.toml`) |
| Git | clone and match CI commits |
| Docker Desktop (optional) | Compose tests, Grid, Playwright CI image |
| Allure CLI (optional) | local `allure serve` |
| TestRail CLI (optional) | channel B in section N2 |

### Section map

| Block | Topic | Code |
|-------|--------|------|
| **I1–I4** | API, mocks, negatives, troubleshooting | `tests/mocks_lab/`, `tests/test_compose_api.py`, `src/lab_fw/api/` |
| **L1–L3** | Distributed concepts, queue/worker, investigation | `src/distributed_lab/`, `tests/distributed_lab/` |
| **M1–M2** | xdist, isolation, Selenium Grid, UI in Docker | `tests/parallel_lab/`, `tests/conftest.py`, Compose profiles |
| **N1–N3** | Allure, TestRail, Jira, risk-based suites | `src/lab_fw/reporting/`, `tests/test_api_client.py`, `pyproject.toml` (markers) |
| **J3** | Mock Device Inventory (cloud, DFU, heartbeat) | `src/device_lab/`, `tests/device_lab/` |
| **O1–O4** | Retry, flaky, quality gates, AI workflow | `retry_policy.py`, `tests.yml`, `tests/README_PYTEST.md` |

Suggested reading order: **Quick start → Layout → I1–I4 → L1 → L2 → L3 → M1 → M2 → N1 → N2 → N3 → J3 → O**. Keep **Docker**, **GitHub Actions**, and **Pytest markers** open for every run.

### Table of contents

1. [Quick start](#quick-start-local)
2. [Layout](#layout)
3. [Environment variables](#environment-variables)
4. [Pytest markers](#pytest-markers)
5. [Docker](#docker)
6. [GitHub Actions](#github-actions)
7. [I1 — API diagram](#api-interaction-diagram-i1) (includes I2–I4)
8. [L1 — glossary](#distributed-systems-theory-and-terms-l1)
9. [L2 — queue and worker](#l2--queue-retry-timeout-deadline-idempotency)
10. [L3 — failure investigation](#l3--failure-investigation-checklist)
11. [M1 — parallelism](#m1--parallel-execution-and-resource-isolation)
12. [M2 — Grid and UI](#m2--remote-browser-selenium-grid-and-ui-in-docker)
13. [N1 — Allure](#n1--allure-reporting)
14. [N2 — TestRail and Jira](#n2--jira--testrail)
15. [N3 — risk-based (smoke / full)](#n3--risk-based-testing-smoke-and-full-regression)
16. [J3 — Device Inventory API (cloud and DFU)](#j3--mock-device-inventory-api-cloud-and-dfu)
17. [O — automation reliability](#o--automation-reliability-retry-flaky-ci-gates-ai)
18. [Allure (short)](#allure-short)
19. [Module documentation](#module-documentation)

### How chapters are structured

Each major section starts with **About this section**: purpose, files to open, and self-check steps. Tables and commands follow. If a test fails, start with [I4](#test-failure-troubleshooting-i4); for infrastructure issues use [L3](#l3--failure-investigation-checklist).
