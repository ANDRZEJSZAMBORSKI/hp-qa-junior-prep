### About this section

Configuration via environment variables and `Settings`. Most MockTransport API tests **do not** need a real token.

### Precedence

1. Explicit test/fixture values.
2. Env (`LAB_FW_*`).
3. Code defaults (`example.com`, 5s timeout).

### Practice

- Locally `LAB_FW_API_TOKEN` may be unset.
- CI **tests** workflow requires the Secret token — typical env drift.
- Compose API tests should pass `http://mock-api:1080` in `Settings`, not a global `LAB_FW_BASE_URL`.

### Self-check

```bash
python -c "from lab_fw.config import get_settings; s=get_settings(); print(s.base_url, s.timeout_s)"
```
