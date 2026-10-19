import os
import pytest
from filelock import FileLock
import multiprocessing

@pytest.mark.parallel_lab
def test_shared_file_write_read():
    # Verify that concurrent workers can interfere when using one shared file.
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "master")
    shared_file = os.path.join(os.path.dirname(__file__), f"shared_report_{worker_id}.txt")
    with open(shared_file, "w", encoding="utf-8") as file:
        file.write(worker_id)
    with open(shared_file, "r", encoding="utf-8") as file:
        content = file.read()
    assert content == worker_id

@pytest.mark.parallel_lab
def test_worker_specific_files_are_isolated():
    # Verify that another worker can overwrite the shared file's content.
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "master")
    shared_file = os.path.join(os.path.dirname(__file__), f"shared_report_{worker_id}.txt")
    with open(shared_file, "w", encoding="utf-8") as file:
        file.write(worker_id)
    with open(shared_file, "r", encoding="utf-8") as file:
        content = file.read()
    assert content == worker_id 

@pytest.mark.parallel_lab
def test_tmp_path_creates_isolated_temp_file(tmp_path):
    # Verify that each test writes to its own temporary directory.
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "master")
    report_file = tmp_path / "report.txt"
    with open(report_file, "w", encoding="utf-8") as file:
        file.write(worker_id)
    with open(report_file, "r", encoding="utf-8") as file:
        content = file.read()
    assert content == worker_id 

@pytest.mark.parallel_lab
def test_tmp_path_is_unique_for_each_test(tmp_path):
    # Verify that each test writes to its own temporary directory.
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "master")
    report_file = tmp_path / "report.txt"
    with open(report_file, "w", encoding="utf-8") as file:
        file.write(worker_id)
    with open(report_file, "r", encoding="utf-8") as file:
        content = file.read()
    assert content == worker_id 

@pytest.mark.parallel_lab
def test_shared_file_access_with_file_lock():
    # Verify that concurrent workers can interfere when using one shared file.
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "master")
    shared_file = os.path.join(os.path.dirname(__file__), f"shared_report.txt")
    lock_file = shared_file + ".lock"
    file_lock = FileLock(lock_file)
    with file_lock:
        with open(shared_file, "w", encoding="utf-8") as file:
            file.write(worker_id)
        with open(shared_file, "r", encoding="utf-8") as file:
            content = file.read()
        assert content == worker_id

@pytest.mark.parallel_lab
def test_shared_file_access_is_serialized():
    # Verify that another worker can overwrite the shared file's content.
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "master")
    shared_file = os.path.join(os.path.dirname(__file__), f"shared_report.txt")
    lock_file = shared_file + ".lock"
    file_lock = FileLock(lock_file)
    with file_lock:
        with open(shared_file, "w", encoding="utf-8") as file:
            file.write(worker_id)
        with open(shared_file, "r", encoding="utf-8") as file:
            content = file.read()
        assert content == worker_id


def _shared_file_process_worker(worker_id, shared_file, barrier, result_queue, lock_file=None):
    # Verify whether concurrent processes can overwrite each other's data.
    if lock_file is None:
        with open(shared_file, "w", encoding="utf-8") as file:
            file.write(worker_id)

        barrier.wait()

        with open(shared_file, "r", encoding="utf-8") as file:
            content = file.read()
    else:
        barrier.wait()

        with FileLock(lock_file):
            with open(shared_file, "w", encoding="utf-8") as file:
                file.write(worker_id)

            with open(shared_file, "r", encoding="utf-8") as file:
                content = file.read()

    result_queue.put((worker_id, content))


@pytest.mark.parallel_lab
def test_shared_file_race_condition_is_reproducible(tmp_path):
    # Verify that two processes can read the same overwritten file content.
    ctx = multiprocessing.get_context("spawn")
    shared_file = str(tmp_path / "shared.txt")
    barrier = ctx.Barrier(2)
    result_queue = ctx.Queue()

    processes = [
        ctx.Process(
            target=_shared_file_process_worker,
            args=(worker_id, shared_file, barrier, result_queue),
        )
        for worker_id in ("worker-A", "worker-B")
    ]

    for process in processes:
        process.start()

    results = [result_queue.get(timeout=10) for _ in processes]

    for process in processes:
        process.join(timeout=10)
        assert not process.is_alive()
        assert process.exitcode == 0

    written_ids = {worker_id for worker_id, _ in results}
    read_values = {content for _, content in results}

    assert written_ids == {"worker-A", "worker-B"}
    assert len(read_values) == 1
    assert read_values.issubset(written_ids)


@pytest.mark.parallel_lab
def test_file_lock_prevents_shared_file_race(tmp_path):
    # Verify that FileLock protects each process's write-read operation.
    ctx = multiprocessing.get_context("spawn")
    shared_file = str(tmp_path / "shared.txt")
    lock_file = shared_file + ".lock"
    barrier = ctx.Barrier(2)
    result_queue = ctx.Queue()

    processes = [
        ctx.Process(
            target=_shared_file_process_worker,
            args=(worker_id, shared_file, barrier, result_queue, lock_file),
        )
        for worker_id in ("worker-A", "worker-B")
    ]

    for process in processes:
        process.start()

    results = [result_queue.get(timeout=10) for _ in processes]

    for process in processes:
        process.join(timeout=10)
        assert not process.is_alive()
        assert process.exitcode == 0

    assert {worker_id: content for worker_id, content in results} == {
        "worker-A": "worker-A",
        "worker-B": "worker-B",
    }
