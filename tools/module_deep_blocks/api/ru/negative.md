### О разделе — Negative / errors

4xx/5xx **не** exception по умолчанию — явный контракт. Transport → `ApiError` с `__cause__`.

**Проверка:** `pytest tests/test_api_negative.py tests/test_compose_api.py -q`
