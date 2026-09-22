# Полный план подготовки: Mid QA Automation (под требования команды HP)

**Кандидат:** Andrzej Szamborski  
**Репо практики:** `hp-qa-junior-prep` (позже по смыслу — automation lab / framework)  
**Нагрузка:** ~40 часов в неделю  
**Цель рынка:** навыки **mid**, чтобы конкурировать за **junior/mid** в серьёзной компании  
**Ориентир по письму руководителя отдела (требования команды)** — закрывать каждый пункт на уровне mid (понимаю + делал + могу объяснить/спроектировать кусок), без претензии на 5+ лет IoT/Bluetooth hardware.

---

## 0. Зачем mid, если вакансия «junior»

На входе в сильные команды на junior часто приходят люди с mid-скиллами.  
План заточен не под «галочки junior», а под:

- умение **строить и развивать** automation framework  
- pytest (fixtures/POM/plugins/hooks/parallel/isolation)  
- UI + API + Allure + CI + Docker  
- git/PR/conflicts  
- risk-based мышление и расследование падений  

IoT / Bluetooth / огромный TestRail (20k кейсов) — продуктовый опыт; закрываем **смысл + mock/матрица рисков**, не притворяемся device-lab инженером без железа.

---

## 1. Критерий «тема сдана» (mid)

Тема закрыта, только если можешь:

1. Объяснить **зачем**  
2. Написать кусок с нуля  
3. Отладить типичный сбой / flake  
4. Сделать PR и пройти свой review-чеклист  
5. Связать с каркасом фреймворка (reuse, слои, config)

Формат учёбы (обязательный стандарт):

1. Зачем шаг  
2. Что меняется (диск / GitHub / отчёт)  
3. Команда или код — с разбором  
4. Проверка глазами (`status`, UI, Allure, CI log)  
5. Только потом следующий шаг  

---

## 2. Срок при 40 ч/нед

| Блок | Ориентир |
|------|----------|
| Git mid (CS50 + мини-проект конфликтов) | 3–5 дней |
| Python for Frameworks + Pytest engine | 2.5–3.5 недели |
| API на каркасе | 1–1.5 недели |
| UI Playwright (+ Selenium) + POM | 2–2.5 недели |
| Allure углубление + GitHub Actions CI | 1.5–2 недели |
| Docker / Compose | ~1 неделя |
| Linux / shell | ~1 неделя |
| Cloud mock + integration | ~1 неделя |
| Parallel / observability / reliability | ~1 неделя |
| TestRail/Jira + risk-based | ~1 неделя |
| IoT/BT theory + device mock | ~1 неделя |
| Полировка репо, софт-mock interviews | ~1 неделя |

**Итого до сильного portfolio:** примерно **12–16 недель** full-time (~3–4 месяца).  
Параллельно лёгкий NeetCode только если не ест ядро фреймворка/CI.

---

## 3. Текущий прогресс (факт)

### Закрыто / почти закрыто

- **Фаза 0:** репо, venv, git local basics  
- **Python foundation (язык):** exceptions, collections, OOP practice, decorators D1–D12, generators G1–G5, context managers CM1–CM4, package management (venv/pip/requirements)  
- **Устный мини по декораторам**  
- **GitHub lab:** remote, push, branch, PR (`gh` + browser), fetch+merge вместо pull  
- **Конфликт color red/blue:** подготовка на feature → push → `gh pr merge` (финиш на master) — понимание добить повторным мини-проектом  

### Сознательно откладывали в декораторах (junior) — теперь В ПЛАНЕ для framework mid

Раньше отложили: pytest plugin, Allure как слой, async+generics senior, production backoff/circuit breaker, metaclasses.

**Включаем в mid/framework:**

- pytest hooks + свой mini-plugin  
- Allure как слой отчёта фреймворка  
- retry с backoff/jitter (util в core)  
- packaging (`pyproject.toml`, editable install)  
- ABC/Protocol, exception hierarchy, logging, config/data layers  

**По-прежнему не тащим (senior/узко):** метаклассы, свой Allure с нуля, полный async-fw, circuit breaker mesh.

### Ближайшие шаги (не прыгать)

1. Лекция CS50 Web Notes 1 (Git): https://cs50.harvard.edu/web/notes/1/  
2. Ещё один мини-проект Git с конфликтами (новый стандарт объяснений)  
3. Только потом — **Python for Frameworks + Pytest**  

---

## 4. Полный план по фазам (подряд)

---

### ФАЗА A — Python language foundation

**Из письма:** OOP, collections, exceptions, decorators, generators, context managers, venv, package management.

| # | Тема | Mid-бар | Статус |
|---|------|---------|--------|
| A1 | venv + pip + requirements | объяснить isolate/freeze vs hand-edit | ✅ |
| A2 | collections | list/dict/set/tuple, comp, Counter/defaultdict по делу | ✅ practice |
| A3 | exceptions | raise/try/except/finally, свои типы позже в PF | ✅ |
| A4 | OOP | classes, inheritance, composition → задел POM | ✅ |
| A5 | decorators | wraps, stack, param, method, class-decorator, register | ✅ D1–D12 + oral |
| A6 | generators | yield, genexp, yield from, take | ✅ G1–G5 |
| A7 | context managers | enter/exit, contextmanager, FakeDriver/temp file | ✅ CM1–CM4 |

**Добивка A после git-мини (коротко):** устный mid-чек + перенос retry/timer/CM в `core/` (не новая теория ради теории).

---

### ФАЗА B — Git / PR / conflicts / reviews

**Из письма:** Git branching, pull requests, code reviews, conflict resolution.

| # | Тема | Mid-бар |
|---|------|---------|
| B1 | commit / branch / remote / push / fetch / merge | без магии, проверка глазами |
| B2 | PR через browser и `gh` | create / view / merge / flags |
| B3 | conflict | общий предок; 1-я ветка без конфликта; 2-я с конфликтом; полуфинал на feature; финиш = merge в mainline |
| B4 | code review чеклист | сам ревьюишь свой PR |

**Сейчас:** CS50 → мини-проект B3/B4 → сдача фазы B.

---

### ФАЗА PF — Python for Frameworks (ОБЯЗАТЕЛЬНО, раньше UI)

**Из письма:** построение и развитие automation framework, reusable libraries, abstraction layers, configuration, test data; плюс pytest plugins/hooks.

Это место, куда вошло то, что откидывали в «просто декораторах».

| # | Тема | Что сделать руками |
|---|------|-------------------|
| PF1 | Package | структура пакета; `pyproject.toml`; `pip install -e .`; импорт `from lab_fw...` |
| PF2 | Abstractions | `ABC` / `Protocol`: BasePage, ApiClient; composition |
| PF3 | Cross-cutting | logging; exception hierarchy; retry+backoff/jitter; timing/log декораторы в `core/` |
| PF4 | Config | settings из env + файл; никаких секретов в git |
| PF5 | Test data | factories/builders; фикстуры данных |
| PF6 | Pytest engine | conftest layers; fixtures для POM; marks; parametrize; **hooks**; **свой plugin**; xdist + isolation rules |
| PF7 | Reporting layer | Allure steps/attachments через обёртки fw |

**Deliverable фазы PF:** каркас репо, который уже «пахнет фреймворком», даже до полного UI.

Пример целевой структуры:

```text
hp-qa-junior-prep/
  pyproject.toml
  src/lab_fw/          # или lab_fw/
    core/              # config, log, retry, errors
    api/
    ui/
    pytest_plugin/     # hooks / plugin
  tests/
  ci/
  docker/
  PLAN_MID_HP.md
```

---

### ФАЗА C — Pytest deep (может идти параллельно/сразу после PF6)

**Из письма:** fixtures (особенно POM), parametrization, markers, plugins, hooks, parallel execution, test isolation, clean code, reusable.

| # | Тема | Mid-бар |
|---|------|---------|
| C1 | fixture scopes + yield teardown | = CM-идея |
| C2 | conftest hierarchy | shared vs local |
| C3 | markers + pytest.ini/pyproject markers | |
| C4 | parametrize + ids | |
| C5 | plugin/hooks (из PF6) | на fail — лог/скрин/артефакт |
| C6 | pytest-xdist | изоляция обязательна |
| C7 | anti-flaky hygiene | нет порядка тестов, нет shared mutable |

---

### ФАЗА E — API automation

**Из письма:** REST, HTTP, JSON, auth/OAuth2, requests/httpx, schema validation.

| # | Тема | Mid-бар |
|---|------|---------|
| E1 | httpx client wrapper | timeouts, ошибки fw |
| E2 | auth | bearer + учебный OAuth2/mock |
| E3 | schema | pydantic или jsonschema |
| E4 | негативные контракты | 4xx/5xx, timeout |
| E5 | retry policy на API | только где оправдано |

---

### ФАЗА D — UI automation + POM

**Из письма:** Selenium / Playwright, Page Object, waits умеренно, locators (лучше ID).

| # | Тема | Mid-бар |
|---|------|---------|
| D1 | Playwright primary | стабильный demo-сайт |
| D2 | Selenium module | уметь читать/писать вторым стеком |
| D3 | POM | BasePage, pages, components; без God-object |
| D4 | waits | explicit; без sleep-политики |
| D5 | locators | ID / test-id first |
| D6 | fixtures POM | driver/page из PF/C |

---

### ФАЗА G — CI/CD + Allure + failure analysis

**Из письма:** GitHub Actions / GitLab / Azure; pipeline; Allure обязательно; parallel jobs; secrets; failure analysis; test configs.

| # | Тема | Mid-бар |
|---|------|---------|
| G1 | GitHub Actions pipeline | install → test → artifacts |
| G2 | secrets | |
| G3 | parallel jobs / xdist в CI | |
| G4 | Allure в CI | отчёт как артефакт |
| G5 | читать упавший job | flake vs bug vs infra |

Один глубокий GH Actions > три пустых YAML «для резюме».

---

### ФАЗА H — Docker

**Из письма:** создание/использование контейнеров, Compose, test environments.

| # | Тема | Mid-бар |
|---|------|---------|
| H1 | Dockerfile тест-рана | |
| H2 | Compose (app/mock + tests) | |
| H3 | тот же suite локально и в контейнере | |

---

### ФАЗА K — Linux / shell

**Из письма:** CLI, processes, permissions, networking basics, logs, shell scripting (очистка логов / fresh install).

| # | Тема | Mid-бар |
|---|------|---------|
| K1 | processes, permissions, pipes | |
| K2 | logs | |
| K3 | networking: ports, curl, DNS basics | |
| K4 | скрипт clean logs + smoke | |

---

### ФАЗА I — Cloud / integration testing

**Из письма:** desktop ≡ cloud checks; REST/HTTP/auth/JSON; app ↔ backend ↔ cloud; logs/envs.

| # | Тема | Mid-бар |
|---|------|---------|
| I1 | схема взаимодействия в README | |
| I2 | mock cloud API | |
| I3 | integration tests | auth fail, timeout |
| I4 | чеклист «где смотреть логи» | |

---

### ФАЗА L — Distributed systems + observability

**Из письма:** async communication, queues/events, retries, timeouts, eventual consistency; logs/metrics/traces; разные envs/builds.

| # | Тема | Mid-бар |
|---|------|---------|
| L1 | теория + термины | |
| L2 | лаба queue/retry/timeout | |
| L3 | чеклист расследования failure | env, build, log, metric, trace |

---

### ФАЗА M — Parallel / remote execution

**Из письма:** test runners, agents, remote execution, resource management.

| # | Тема | Mid-бар |
|---|------|---------|
| M1 | xdist ресурсы (браузеры/порты) | |
| M2 | optional remote browser/grid | после Docker |

---

### ФАЗА N — Reporting + test management + risk-based

**Из письма:** Allure; Feature milestones TR; analytics; Jira + TestRail; risk-based из огромной матрицы.

| # | Тема | Mid-бар |
|---|------|---------|
| N1 | Allure analytics hygiene | |
| N2 | Jira + TestRail trial | milestone, case ↔ autotest id |
| N3 | risk-based отбор suite | обосновать smoke vs full |

---

### ФАЗА J — IoT / devices / Bluetooth (продуктовый слой)

**Из письма:** desktop/mobile/cloud/devices; Windows/macOS/iOS/Android; Bluetooth; firmware; DFU; Cloud Device Inventory.

| # | Тема | Mid-бар (честный) |
|---|------|-------------------|
| J1 | теория DFU / inventory / BT flake risks | |
| J2 | test matrix device × platform | |
| J3 | mock device API + states | online/offline/DFU |
| J4 | формулировка на собесе | что умеешь сейчас vs что нарастишь на продукте |

Hands-on BT без железа — не блокер плана; не врать в резюме.

---

### ФАЗА O — Reliability + modern QA + AI-assisted

**Из письма:** flaky detection; retries где оправдано; isolation; shift-left; quality gates; LLM с верификацией.

| # | Тема | Mid-бар |
|---|------|---------|
| O1 | политика retry | не маскировать баги продукта |
| O2 | quarantine / mark flaky | |
| O3 | quality gate в CI | |
| O4 | AI | черновик → прогон/правка → только потом merge |

---

## 5. Порядок выполнения (строго)

```text
B (CS50 + git conflict mini)
 → PF1…PF7 + C (framework + pytest engine)
 → E (API)
 → D (UI + POM)
 → G (CI + Allure deep)
 → H (Docker)
 → K (Linux/shell)
 → I (Cloud mock)
 → L + M (distributed + parallel/remote)
 → N (TestRail/risk)
 → J (IoT/BT theory + mock)
 → O (reliability + gates + AI hygiene)
 → полировка репо + mock interviews
```

---

## 6. Недельный ритм при 40 ч

Пример распределения:

- 24–28 ч — практика кода / CI / лабы  
- 6–8 ч — теория + конспект своими словами  
- 4–6 ч — NeetCode/light algorithms (не вместо pytest)  
- 2 ч — ревью своего PR / README / Allure отчёта  

Каждая неделя: **1 PR в учебный репо** + короткое «что сдано / что нет».

---

## 7. Definition of Done всего трека

Можешь открыть GitHub и сказать:

> Это мой automation framework: installable package, core (config/log/retry/errors), pytest plugin/hooks, API client, Playwright POM, Allure, GitHub Actions, Docker.  
> Тесты изолированы, parallel через xdist, flaky-политика явная.  
> Risk-based отбор и расследование падений по env/build/logs.  
> Cloud/device — контракты и mock + матрица рисков; готов наращивать на вашем стеке.

Это **mid-история** на вакансию Junior/Mid QA Automation.

---

## 8. Связь с письмом руководителя (чеклист покрытия)

| Пункт письма | Фазы плана |
|--------------|------------|
| Python OOP… package management | A + PF |
| Pytest fixtures… isolation… reusable | PF + C |
| Selenium/Playwright POM waits locators | D |
| API REST… schema | E |
| Test architecture framework… | PF + F-структура |
| CI/CD Allure secrets parallel | G |
| Git branching PR conflicts | B |
| Docker Compose | H |
| Cloud integration | I |
| IoT/Bluetooth/devices | J |
| Linux shell | K |
| Distributed queues retries consistency | L |
| Observability | L |
| Parallel/remote execution | M + C6 |
| Reporting Allure TR analytics | G + N |
| Jira TestRail risk-based | N |
| Automation reliability flaky | O + C7 |
| Modern QA shift-left gates | O |
| AI-assisted with verification | O4 |

---

## 9. Правила тренера/ученика (зафиксировано)

- Ничего не «закрыто», пока нет понимания финиша (пример: conflict fix на feature ≠ смена master без merge PR).  
- Не прыгать фазами.  
- Не junior-урезать framework-темы: plugins/hooks/packaging/// abstractions — в плане.  
- Senior-зоопарк не раздувать.  

---

*Документ живой: обновлять статусы ✅/🔄/⬜ по мере сдачи фаз.*
