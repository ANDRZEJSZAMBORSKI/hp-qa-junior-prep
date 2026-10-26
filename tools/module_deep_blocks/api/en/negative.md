#### About this section — Negative / errors

4xx/5xx are **not** exceptions by default — explicit contract. Transport failures → `ApiError` with `__cause__`.

**Check:** `pytest tests/test_api_negative.py tests/test_compose_api.py -q`
