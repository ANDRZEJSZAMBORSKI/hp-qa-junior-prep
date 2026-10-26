### О разделе

Два pipeline дополняют друг друга: быстрая обратная связь на runner и полный интеграционный прогон в Docker.

### tests.yml

- Установка зависимостей на ubuntu runner.
- pytest с xdist, **без** ui/selenium/compose.
- Artifact `allure-results` — частичный срез.

### ci.yml

- Полный Compose: API → down → Selenium (parallel + serial) → Playwright (parallel + serial).
- Один aggregated `allure-results` после всех стадий.

### Как учиться по Actions

1. Открой упавший job → step log.
2. Скачай artifact Allure.
3. Сравни команду pytest с локальной из README.

### Самопроверка

Fork + push → зелёный **tests** на каждом PR; **CI** длиннее, но даёт полную картину.
