#### About this section — Schema

`parse_user` / `parse_token` centralize JSON validation → `SchemaError` instead of KeyError in every test.

**Check:** `pytest tests/test_api_schemas.py -q`
