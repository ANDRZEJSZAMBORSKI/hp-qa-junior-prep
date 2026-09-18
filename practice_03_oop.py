class TestCase:
    def __init__(self,
                id: str,
                feature: str,
                priority: str,
                automated: bool) -> None:
        self._id = id
        self._feature = feature
        self._priority = priority
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

    @property
    def automated(self):
        return self._automated

    def summary(self) -> str:
        return f"{self.id} [{self.priority}] {self.feature} auto={self.automated}"


def main():
    tc = TestCase("TC001", "login", "critical", True)
    assert tc.summary() == "TC001 [critical] login auto=True"
    print("O1 OK")

if __name__ == "__main__":
    main()
    
    
        