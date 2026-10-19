
import httpx
import pytest

from lab_fw.api.client import ApiClient, HttpStatusError
from distributed_lab.queue_worker import InMemoryQueue, Worker, parse_job


@pytest.mark.distributed_lab
def test_l3_retry_investigation(settings, caplog: pytest.LogCaptureFixture):
    # Investigate retry behavior by comparing API attempts, response status, and retry logs.
    caplog.set_level("WARNING", logger="lab_fw.core.retry")
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            return httpx.Response(503, request=request)

        return httpx.Response(
            200,
            json={"ok": True},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(parse_job({"method": "GET", "path": "/users"}))

        worker = Worker(queue, client)
        response = worker.run_once()

    assert attempts == 3
    assert response.status_code == 200
    assert response.json() == {"ok": True}


    warnings = [
        record
        for record in caplog.records
        if record.name == "lab_fw.core.retry"
        and record.levelname == "WARNING"
    ]

    assert len(warnings) == 2
    assert "attempt 1/3 failed" in warnings[0].message
    assert "attempt 2/3 failed" in warnings[1].message
    assert all("HTTP 503" in record.message for record in warnings)

@pytest.mark.distributed_lab
def test_l3_retry_investigation_exhausted(settings, caplog: pytest.LogCaptureFixture):
    # Investigate retry behavior by comparing API attempts, response status, and retry logs.
    caplog.set_level("WARNING", logger="lab_fw.core.retry")
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        
        return httpx.Response(503, request=request)

    

    transport = httpx.MockTransport(handler)

    with ApiClient(settings, transport=transport) as client:
        queue = InMemoryQueue()
        queue.put(parse_job({"method": "GET", "path": "/users"}))

        worker = Worker(queue, client)
        with pytest.raises(HttpStatusError, match="failed with HTTP 503") as exc_info:
            worker.run_once()

    assert attempts == 3
    assert exc_info.value.response.status_code == 503
    assert exc_info.value.response.request.method == "GET"
    assert exc_info.value.response.request.url.path == "/users"


    warnings = [
        record
        for record in caplog.records
        if record.name == "lab_fw.core.retry"
        and record.levelname == "WARNING"
    ]

    assert len(warnings) == 2
    assert "attempt 1/3 failed" in warnings[0].message
    assert "attempt 2/3 failed" in warnings[1].message
    assert all("HTTP 503" in record.message for record in warnings)
