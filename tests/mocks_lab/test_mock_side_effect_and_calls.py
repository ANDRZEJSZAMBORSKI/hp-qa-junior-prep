import pytest
from functools import wraps
from unittest.mock import Mock
from lab_fw.core.errors import ApiError
import logging
from lab_fw.core.retry import retry_call

retry_logger = logging.getLogger("lab_fw.core.retry")

def retry(times: int = 3, exc_types=(Exception,)):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            for i in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exc_types as e:
                    retry_logger.warning("attempt %s/%s failed: %s", i, times, e)
                    last = e
            raise last
        return wrapper
    return  decorator

@pytest.mark.mocks_pure
@pytest.mark.mocks
def test_call_retry():

    client = Mock()
    client.get.side_effect = [
                                ApiError("tmp"),
                                ApiError("tmp"),
                                "ok",
                            ]

    @retry(exc_types= (ApiError,))
    def call_retry():
        return client.get()

    assert call_retry() == "ok"
    assert client.get.call_count == 3

@pytest.mark.mocks_pure
@pytest.mark.mocks
def test_retry_call():
    client = Mock()
    client.get.side_effect = [
                            ApiError("tmp"),
                            ApiError("tmp"),
                            "ok",
                        ]
    assert retry_call(client.get, delay_s = 0, retry_on = (ApiError,)) == "ok"
    assert client.get.call_count == 3

@pytest.mark.mocks_pure
@pytest.mark.mocks
def test_retry_error():
    client = Mock()
    client.get.side_effect = [
                            ValueError("tmp"),
                        ]
    with pytest.raises(ValueError, match="tmp"):
        retry_call(client.get, attempts = 1, delay_s = 0, retry_on = (ApiError,))
    assert client.get.call_count == 1

@pytest.mark.mocks_pure
@pytest.mark.mocks
def test_call_retry_error():
    client = Mock()
    client.get.side_effect = [
                                ValueError("tmp"),
                            ]
    @retry(times=1, exc_types= (ApiError,))
    def call_retry_error():
        return client.get()
    
    with pytest.raises(ValueError, match="tmp"):
        call_retry_error()
    assert client.get.call_count == 1
