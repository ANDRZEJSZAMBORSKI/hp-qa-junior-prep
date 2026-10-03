from unittest.mock import MagicMock, patch
import pytest
from lab_fw.ui.client import UIClient

@pytest.mark.ui
def test_ui_client(settings):
    with UIClient(settings) as ui:
        ui.page.goto("/login")
        assert ui.page.url == f"{settings.ui_base_url}/login"

@pytest.mark.ui
def test_ui_client_applies_ui_timeout(settings):
    ms = int(settings.ui_timeout_s * 1000)
    with patch("lab_fw.ui.client.sync_playwright") as sp:
        pw = MagicMock()
        browser = MagicMock()
        context = MagicMock()
        page = MagicMock()
        sp.return_value.start.return_value = pw
        pw.chromium.launch.return_value = browser
        browser.new_context.return_value = context
        context.new_page.return_value = page
        ui = UIClient(settings)
        ui.start()
        page.set_default_navigation_timeout.assert_called_with(ms)
        page.set_default_timeout.assert_called_with(ms)
        ui.close()