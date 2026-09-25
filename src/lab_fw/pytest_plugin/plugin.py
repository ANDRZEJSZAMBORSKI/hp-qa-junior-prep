import logging
import pytest
import re
from pathlib import Path

WINDOWS_BAD = r'[\\/:*?"<>|]'
def _safe_nodeid(nodeid: str) -> str:
    return re.sub(r'_+', '_', re.sub(WINDOWS_BAD, '_', nodeid.strip()))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """After pytest builds the test report, log failures."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        artifacts_enabled = item.config.getoption("--lab-fw-artifacts")
        file_name = _safe_nodeid(item.nodeid)
        if artifacts_enabled:
            artifacts_dir = item.config.getoption("--lab-fw-artifacts-dir")
            artifacts_dir_path = Path(artifacts_dir)
            artifacts_dir_path.mkdir(parents=True, exist_ok=True)
            path = Path(artifacts_dir) / file_name
            with path.open("w", encoding="utf-8") as file:
                file.write(f"nodeid: {item.nodeid}\n")
                file.write(f"{report.longrepr}\n")
        logging.getLogger("lab_fw.pytest").error(
            "FAILED %s: %s",
            item.nodeid,
            report.longrepr,
        )

def pytest_addoption(parser):
    group = parser.getgroup("lab-fw")

    group.addoption(
        "--lab-fw-artifacts",
        action="store_true",
        default=False,
        help="Write text artifacts for failed tests.",
    )

    group.addoption(
        "--lab-fw-artifacts-dir",
        action="store",
        default=".lab_fw_artifacts",
        help="Directory for failure artifacts.",
    )