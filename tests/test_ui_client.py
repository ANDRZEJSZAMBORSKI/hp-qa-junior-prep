import pytest

from lab_fw.ui.client import UIClient

@pytest.mark.ui
def test_ui_client(settings):
    with UIClient(settings) as ui:
        ui.page.goto("/login")
        assert ui.page.url == f"{settings.ui_base_url}/login"