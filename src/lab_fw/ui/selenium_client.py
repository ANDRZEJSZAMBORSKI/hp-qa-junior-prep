from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from lab_fw.core.config import Settings
from lab_fw.core.errors import UiError

class SeleniumClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._driver: WebDriver | None = None
        
    @property
    def settings(self) -> Settings:
        return self._settings

    @settings.setter
    def settings(self, value: Settings):
        if not value.ui_base_url:
            raise UiError("LAB_FW_UI_BASE_URL cannot be empty.")
        self._settings = value

    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            raise UiError("Selenium client is not started.")
        return self._driver

    def start(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-features=PasswordLeakDetection")
        options.add_experimental_option(
                                            "prefs",
                                            {
                                                "credentials_enable_service": False,
                                                "profile.password_manager_enabled": False,
                                                "profile.password_manager_leak_detection": False,
                                            },
                                        )
        self._driver = webdriver.Chrome(options=options)

    def __enter__(self):
        self.start()
        return self

    def close(self) -> None:
        if self._driver:
            self._driver.quit()
        self._driver = None

    def __exit__(self, exc_type, exc, tb):
        self.close()