### О разделе

Углубление по подсистемам `lab_fw` и pytest. Корневой README — карта; модульные README — API контрактов, UI стеки, reporting decorators.

### Рекомендуемый порядок

1. [API](src/lab_fw/api/README.md) — клиент и ошибки.
2. [Device lab](tests/device_lab/README.md) — облачный inventory, DFU, MockTransport.
3. [Mocks lab](tests/mocks_lab/README.md) — швы подмены.
4. [Reporting](src/lab_fw/reporting/README.md) — Allure слой.
5. [UI](src/lab_fw/ui/README.md) — Playwright/Selenium.
6. [Pytest plugin](src/lab_fw/pytest_plugin/README.md) — hooks.
7. [README_PYTEST](tests/README_PYTEST.md) — изоляция и hygiene тестов.
