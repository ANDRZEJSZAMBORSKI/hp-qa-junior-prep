#### O sekcji — Retry policy

Retry tylko przez `retry_call`, nie wewnątrz każdego `get`. Tabela poniżej to źródło prawdy dla L1 pkt 3 i workera L2.

**Sprawdzenie:** `pytest tests/test_api_retry_policy.py -q`
