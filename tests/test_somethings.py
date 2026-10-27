import pytest

@pytest.mark.regression
@pytest.mark.skip(reason="Temporarily disabled")
def test_something():
    assert False, "G5 intentional fail"