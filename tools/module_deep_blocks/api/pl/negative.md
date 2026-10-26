#### O sekcji — Negative / errors

4xx/5xx **domyślnie nie** rzucają wyjątku — jawny kontrakt. Transport → `ApiError` z `__cause__`.

**Sprawdzenie:** `pytest tests/test_api_negative.py tests/test_compose_api.py -q`
