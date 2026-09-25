import pytest

pytest_plugins = ["pytester"]

def test_failure_is_logged(pytester, caplog):
    test_file = pytester.makepyfile(
                                        """
                                        def test_failure():
                                            assert 1 == 2
                                        """
                                    )
    with caplog.at_level("ERROR", logger="lab_fw.pytest"):
        result = pytester.runpytest(test_file)
    result.stdout.fnmatch_lines([
                                    "*FAILED*test_failure*",
                                ])
    assert "FAILED" in caplog.text
    assert "test_failure_is_logged.py::test_failure" in caplog.text

def test_failure_writes_artifact(pytester):
    test_file = pytester.makepyfile(
                                        """
                                        def test_failure():
                                            assert 1 == 2
                                        """
                                    )

    artifacts_dir = pytester.path / "artifacts"

    result = pytester.runpytest(
                                    test_file,
                                    "--lab-fw-artifacts",
                                    f"--lab-fw-artifacts-dir={artifacts_dir}",
                                )

    assert result.ret != 0
    assert artifacts_dir.exists()

    artifact_files = list(artifacts_dir.iterdir())
    assert len(artifact_files) == 1

    content = artifact_files[0].read_text(encoding="utf-8")

    assert "nodeid:" in content
    assert "test_failure_writes_artifact.py::test_failure" in content
    assert "AssertionError" in content


def test_failure_not_writes_artifact(pytester):
    test_file = pytester.makepyfile(
                                        """
                                        def test_failure():
                                            assert 1 == 2
                                        """
                                    )

    artifacts_dir = pytester.path / "artifacts"

    result = pytester.runpytest(
                                    test_file,
                                )

    assert result.ret != 0
    assert not artifacts_dir.exists()

def test_pass_does_not_write_artifact(pytester):

    test_file = pytester.makepyfile(
                                        """
                                        def test_failure():
                                            assert 1 == 1
                                        """
                                    )

    artifacts_dir = pytester.path / "artifacts"

    result = pytester.runpytest(
                                    test_file,
                                    "--lab-fw-artifacts",
                                    f"--lab-fw-artifacts-dir={artifacts_dir}",
                                )

    assert result.ret == 0
    assert not artifacts_dir.exists()
