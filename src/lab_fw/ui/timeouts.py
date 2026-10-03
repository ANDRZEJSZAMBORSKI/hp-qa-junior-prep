from lab_fw.core.config import get_settings


def ui_timeout_s() -> float:
    """Seconds — Selenium / WebDriverWait."""
    return get_settings().ui_timeout_s


def ui_timeout_ms() -> int:
    """Milliseconds — Playwright."""
    return int(get_settings().ui_timeout_s * 1000)