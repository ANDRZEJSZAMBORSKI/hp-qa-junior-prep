### О разделе

Docker воспроизводит CI локально: один образ `tests`, сервис MockServer, опционально Grid и Playwright.

### Mental model

1. **Образ `ci`** — pytest в Linux-контейнере.
2. **Compose network** — `tests` резолвит `mock-api` по DNS.
3. **Profiles** — UI не стартует по умолчанию (экономия ресурсов).

### Когда нужен `DOCKER_TARGET=local`

Корпоративный MITM (Avast и т.п.): target **local** кладёт CA в образ. Файл `avast-root.crt` только на твоей машине.

### Самопроверка

```bash
docker compose up --build --abort-on-container-exit tests
```

Exit code 0 и лог pytest с passed compose-тестами.

### Типичные ошибки

- Запуск compose-тестов на голом `pytest` без `mock-api`.
- Путаница CMD образа (включает compose) vs workflow **tests** (исключает).
