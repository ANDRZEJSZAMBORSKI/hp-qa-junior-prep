import pytest

from lab_fw.ui.timeouts import ui_timeout_ms, ui_timeout_s


@pytest.mark.config
@pytest.mark.smoke
def test_ui_timeout_defaults():
    assert ui_timeout_s() == 120.0
    assert ui_timeout_ms() == 120_000


@pytest.mark.config
def test_ui_timeout_from_env(monkeypatch):
    monkeypatch.setenv("LAB_FW_UI_TIMEOUT_S", "90")
    assert ui_timeout_s() == 90.0
    assert ui_timeout_ms() == 90_000