import pytest
from lab_fw.abstractions import BasePage, HttpClientProtocol
from lab_fw.api.client import ApiClient

class GoodClient:
    
    def get(self, path, **kwargs):
        pass

    def post(self, path, **kwargs):
        pass

    def close(self):
        pass

class BadClient:

    def post(self, path, **kwargs):
        pass

    def close(self):
        pass

@pytest.mark.smoke
@pytest.mark.api
def test_HttpClientProtocol_isinstance():
    assert isinstance(GoodClient(), HttpClientProtocol)
    assert not isinstance(BadClient(), HttpClientProtocol)
    with ApiClient() as client:
        assert isinstance(client, HttpClientProtocol)

class DummyPage(BasePage):

    @property
    def path(self):
        return "/login"

    def open(self):
        return self.path

@pytest.mark.smoke
@pytest.mark.api
def test_BasePage_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BasePage()

@pytest.mark.smoke
@pytest.mark.api
def test_DummyPage():
    page = DummyPage()

    assert page.path == "/login"
    assert page.open() == "/login"