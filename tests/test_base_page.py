from unittest.mock import MagicMock, patch
import pytest

from lab_fw.ui.base_page import BasePage


class _DummyPage(BasePage):
    @property
    def path(self):
        return "/login"


@pytest.mark.smoke
def test_base_page_open_passes_ui_timeout_to_goto():
    page = MagicMock()
    with patch("lab_fw.ui.base_page.ui_timeout_ms", return_value=90_000):
        _DummyPage(page).open()

    page.goto.assert_called_once_with(
        "/login",
        wait_until="domcontentloaded",
        timeout=90_000,
    )