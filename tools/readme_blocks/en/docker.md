### About this section

Docker reproduces CI locally: a `tests` image, MockServer, optional Grid/Playwright.

### Mental model

1. **`ci` image** — pytest on Linux.
2. **Compose network** — `tests` resolves `mock-api`.
3. **Profiles** — UI is opt-in.

### `DOCKER_TARGET=local`

Corporate MITM: **local** target adds your CA; `avast-root.crt` stays untracked.

### Self-check

```bash
docker compose up --build --abort-on-container-exit tests
```

### Common mistakes

- Running `compose` tests without `mock-api`.
- Confusing image CMD (runs compose) with **tests** workflow (excludes compose).
