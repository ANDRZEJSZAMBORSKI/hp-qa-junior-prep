#### O sekcji — Schema

`parse_user` / `parse_token` centralizują walidację JSON → `SchemaError` zamiast KeyError w każdym teście.

**Sprawdzenie:** `pytest tests/test_api_schemas.py -q`
