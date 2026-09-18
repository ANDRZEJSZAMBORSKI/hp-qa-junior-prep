priorities = {"critical", "high", "medium", "low"}

class TestCase:
    def __init__(self,
                id: str,
                feature: str,
                priority: str,
                automated: bool) -> None:
        self._id = id
        self._feature = feature
        self.priority = priority
        self._automated = automated

    @property
    def id(self):
        return self._id

    @property
    def feature(self):
        return self._feature

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, priority: str):
        if not isinstance(priority, str):
            raise TypeError(f"Invalid type {priority} - {type(priority)}: must be 'str'")
        if priority not in priorities:
            raise ValueError(f"Invalid priority: {priority} - must be one from {priorities}")
        self._priority = priority

    @property
    def automated(self):
        return self._automated

    def summary(self) -> str:
        return f"{self.id} [{self.priority}] {self.feature} auto={self.automated}"


class BasePage:
    def __init__(self, driver: str):
        self._driver = driver

    @property
    def driver(self):
        return self._driver

    def open(self, url: str) -> str:
        return f"{self.driver}: open {url}"

    def click(self, locator: str) -> str:
        return f"{self.driver}: click {locator}"

class LoginPage(BasePage):
    def login(self, username: str, password: str) -> str:
        self.click(username)
        return f"{self.driver}: login {username}/{password}"

def main():
    tc = TestCase("TC001", "login", "critical", True)
    assert tc.summary() == "TC001 [critical] login auto=True"
    print("O1 OK")

    tc = TestCase("TC001", "login", "critical", True)
    assert tc.priority == "critical"
    tc.priority = "high"
    assert tc.priority == "high"
    try:
        tc.priority = "urgent"
        assert False
    except ValueError as e:
        assert "Invalid priority" in str(e)
    try:
        TestCase("TC002", "dfu", "asap", True)
        assert False
    except ValueError:
        pass
    print("O2 OK")

    page = LoginPage("chrome")
    assert isinstance(page, BasePage)
    assert page.open("/login") == "chrome: open /login"
    assert page.click("#submit") == "chrome: click #submit"
    assert page.login("ann", "secret") == "chrome: login ann/secret"
    print("O3 OK")

if __name__ == "__main__":
    main()
    
    
        