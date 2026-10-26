### О разделе — Retry policy

Retry только через `retry_call`, не внутри каждого `get`. Таблица ниже — источник истины для L1 п.3 и L2 worker.

**Проверка:** `pytest tests/test_api_retry_policy.py -q`
