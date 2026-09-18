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

if __name__ == "__main__":
    main()
    
    
        