### O tym rozdziale

Konfiguracja przez env i `Settings`. Większość testów MockTransport **nie wymaga** prawdziwego tokenu.

### Kolejność

1. Wartość w teście/fixture.
2. Env (`LAB_FW_*`).
3. Domyślne w kodzie.

### Praktyka

- Lokalnie token może być pusty.
- W CI workflow **tests** token ze Secrets jest wymagany.
- Testy Compose: `http://mock-api:1080` w `Settings`.

### Samokontrola

```bash
python -c "from lab_fw.config import get_settings; s=get_settings(); print(s.base_url, s.timeout_s)"
```
