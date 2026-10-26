### O tym rozdziale

Docker odtwarza CI lokalnie: obraz `tests`, MockServer, opcjonalnie Grid/Playwright.

### Model

1. Obraz **ci** — pytest w Linuxie.
2. Sieć Compose — `mock-api` po DNS.
3. Profile — UI opcjonalnie.

### `DOCKER_TARGET=local`

MITM — target **local** + `avast-root.crt` lokalnie.

### Samokontrola

`docker compose up --build --abort-on-container-exit tests`

### Błędy

- Compose bez `mock-api`.
- Mylenie CMD obrazu z workflow **tests**.
