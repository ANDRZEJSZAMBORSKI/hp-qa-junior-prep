### About this section

Two pipelines: fast feedback on the runner and full integration in Docker.

### tests.yml

- ubuntu runner, xdist pytest, **no** ui/selenium/compose.
- Partial `allure-results` artifact.

### ci.yml

- Full Compose chain including Selenium and Playwright stages.
- Combined `allure-results`.

### Learning from Actions

1. Failed job → step log.
2. Download Allure artifact.
3. Compare pytest command with local README.

### Self-check

Green **tests** on each push; **CI** is slower but complete.
