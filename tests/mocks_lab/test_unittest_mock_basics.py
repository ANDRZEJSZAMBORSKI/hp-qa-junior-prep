from unittest.mock import Mock, call
import pytest
import logging

logger = logging.getLogger("lab_fw.mocks_lab")

@pytest.mark.mocks
def test_mock():
    client = Mock()

    client.get.return_value = 'hello'

    assert client.get() == 'hello'
    client.get.assert_called_once()

    client.get.side_effect = ["a", "b", Exception("x")]
    assert client.get("/a") == 'a'
    assert client.get("/b") == 'b'
    with pytest.raises(Exception, match="x"):
        client.get("/fail")

    assert client.get.call_count == 4
    assert client.get.call_args_list == [
        call(),
        call("/a"),
        call("/b"),
        call("/fail"),
    ]

    logger.info("mock get called %d times", client.get.call_count)