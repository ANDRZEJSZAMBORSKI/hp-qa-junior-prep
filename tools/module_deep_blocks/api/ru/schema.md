### О разделе — Schema

`parse_user` / `parse_token` централизуют валидацию JSON → `SchemaError` вместо KeyError в каждом тесте.

**Проверка:** `pytest tests/test_api_schemas.py -q`
