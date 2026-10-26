### О разделе

Конфигурация через переменные окружения и `Settings`. Большинство API-тестов с MockTransport **не требуют** реального токена.

### Приоритет

1. Явный аргумент / fixture в тесте.
2. Env (`LAB_FW_*`).
3. Значения по умолчанию в коде (`example.com`, timeout 5s).

### Практика

- Локально можно не задавать `LAB_FW_API_TOKEN` — многие тесты пройдут.
- В CI workflow **tests** токен **обязателен** (Secret) — пример расхождения env.
- Для Compose API используй `http://mock-api:1080` в `Settings`, а не глобальный `LAB_FW_BASE_URL`.

### Самопроверка

```bash
python -c "from lab_fw.config import get_settings; s=get_settings(); print(s.base_url, s.timeout_s)"
```
