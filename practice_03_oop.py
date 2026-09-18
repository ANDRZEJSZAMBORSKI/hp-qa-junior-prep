import inspect

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

    @classmethod
    def from_dict(cls, data: dict) -> "TestCase":
        if not isinstance(data, dict):
            raise ValueError("Invalid data type: must be dict")
        if not data or data == {}:
            raise ValueError("Invalid data: empty dictionary")
        params = inspect.signature(cls.__init__).parameters
        if not set(data.keys()).issubset(params.keys()):
            raise ValueError("Invalid data: the dictionary contains unknown parameters.")
        required = {
                    name
                    for name, param in params.items()
                    if name != "self"
                    and param.default is inspect.Parameter.empty
                }
        if not required.issubset(data.keys()):
            raise ValueError("Invalid data: required parameters are missing")
        for key in data:
            if params[key].annotation is not inspect.Parameter.empty and not isinstance(data[key], params[key].annotation):
                raise TypeError(f"Invalid type for {data[key]}: must be {params[key].annotation}")
        return cls(**data)

    @staticmethod
    def normalize_feature(raw: str) -> str:
        return str(raw).strip().lower()

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

class Header:
    def __init__(self, driver: str):
        self._driver = driver

    @property
    def driver(self):
        return self._driver

    def open_menu(self) -> str:
        return f"{self.driver}: open menu"

class HomePage(BasePage):
    def __init__(self, driver: str):
        super().__init__(driver)
        self._header = Header(self.driver)

    @property
    def header(self):
        return self._header

    def open_menu(self) -> str:
        return self.header.open_menu()

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

    home = HomePage("chrome")
    assert home.header.open_menu() == "chrome: open menu"
    assert home.open_menu() == "chrome: open menu"
    assert isinstance(home.header, Header)
    print("O4 OK")

    data = {
        "id": "TC010",
        "feature": "dfu",
        "priority": "critical",
        "automated": True,
    }
    tc = TestCase.from_dict(data)
    assert isinstance(tc, TestCase)
    assert tc.id == "TC010"
    assert tc.summary() == "TC010 [critical] dfu auto=True"
    # валидация priority всё ещё работает
    try:
        TestCase.from_dict({**data, "priority": "asap"})
        assert False
    except ValueError:
        pass
    print("O5 OK")

    assert TestCase.normalize_feature("  Login  ") == "login"
    assert TestCase.normalize_feature("DFU") == "dfu"
    # можно использовать вместе с from_dict
    data = {
        "id": "TC011",
        "feature": TestCase.normalize_feature("  AuTh  "),
        "priority": "high",
        "automated": True,
    }
    tc = TestCase.from_dict(data)
    assert tc.feature == "auth"
    print("O6 OK")

    steps: list[str] = []
    data = {
    "id": "TC011",
    "feature": TestCase.normalize_feature("  AuTh  "),
    "priority": "high",
    "automated": True,
}
    tc = TestCase.from_dict(data)
    page = LoginPage("chrome")
    steps.append(page.open("/login"))
    steps.append(page.login("ann", "secret"))
    home = HomePage("chrome")
    steps.append(home.open_menu())
    assert steps[0] == "chrome: open /login"
    assert "login ann/secret" in steps[1]
    assert steps[2] == "chrome: open menu"
    assert "TC" in tc.summary()
    print("O7 OK")

if __name__ == "__main__":
    main()
    
    
        