import pytest

shared_state = []

@pytest.mark.skip(reason="Demonstration of shared mutable module state.")
def test_shared_state_bad():
    shared_state.append("test")
    assert shared_state == ["test"]

@pytest.fixture
def isolated_state():
    state = []
    yield state

def test_isolated_state(isolated_state):
    isolated_state.append("test")

    assert isolated_state == ["test"]