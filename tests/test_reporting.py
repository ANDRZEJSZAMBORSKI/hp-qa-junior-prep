from lab_fw.reporting import step, attach_text, attach_json, epic, feature, severity, title, description, SeverityLevel
import pytest
import lab_fw.reporting.allure_tools as allure_tools
import json
from contextlib import contextmanager

@pytest.mark.reporting
def test_step():
    with step("test step"):
        value = 1 + 1

    assert value == 2

@pytest.mark.reporting
def test_attach_text():
    attach_text("test text", "Hello from test")

@pytest.mark.reporting
def test_attach_json():
    data = {
        "status": 200,
        "user": "john",
    }

    attach_json("response", data)

@pytest.mark.reporting
def test_epic_without_allure(monkeypatch):
    monkeypatch.setattr(
                            allure_tools,
                            "allure",
                            None,
                        )

    def sample_test():
        return "OK"

    decorated_test = epic("User Management")(sample_test)
    result = decorated_test()
    assert result == "OK"


@pytest.mark.reporting
def test_epic_with_allure(monkeypatch):
    captured = {}

    def fake_epic(value):
        captured["value"] = value

        def decorator(fn):
            return fn

        return decorator

    monkeypatch.setattr(
        allure_tools.allure,
        "epic",
        fake_epic,
    )

    def sample_test():
        return "OK"

    decorated_test = epic("User Management")(sample_test)

    assert captured["value"] == "User Management"
    assert decorated_test() == "OK"


@pytest.mark.reporting
@pytest.mark.parametrize(
                            "decorator, value",
                            [
                                (epic, "User Management"),
                                (feature, "User Management"),
                                (severity, SeverityLevel.CRITICAL),
                                (title, "User Management"),
                                (description, "User Management"),
                            ],
                        )
def test_decorators_without_allure(monkeypatch, decorator, value):
    monkeypatch.setattr(
                            allure_tools,
                            "allure",
                            None,
                        )

    def sample_test():
        return "OK"

    decorated_test = decorator(value)(sample_test)
    result = decorated_test()
    assert result == "OK"

@pytest.mark.reporting
@pytest.mark.parametrize(
                            "decorator, value",
                            [
                                (epic, "User Management"),
                                (feature, "User Management"),
                                (severity, SeverityLevel.CRITICAL),
                                (title, "User Management"),
                                (description, "User Management"),
                            ],
                        )
def test_decorators_with_allure(monkeypatch, decorator, value):
    captured = {}

    def fake_decorator(value):
        captured["value"] = str(value)

        def decorator(fn):
            return fn

        return decorator

    monkeypatch.setattr(
        allure_tools.allure,
        decorator.__name__,
        fake_decorator,
    )

    def sample_test():
        return "OK"

    decorated_test = decorator(value)(sample_test)

    expected_value = (
                            value.value if isinstance(value, SeverityLevel) else value
                        )

    assert captured["value"] == expected_value
    assert decorated_test() == "OK"    

@pytest.mark.reporting
def test_attach_text_with_allure(monkeypatch):
    captured = {}

    def fake_attach(body, name, attachment_type):
        captured["body"] = body
        captured["name"] = name
        captured["attachment_type"] = attachment_type

    monkeypatch.setattr(allure_tools.allure, "attach", fake_attach)

    attach_text("response", "Hello")

    assert captured["body"] == "Hello"
    assert captured["name"] == "response"
    assert captured["attachment_type"] == allure_tools.allure.attachment_type.TEXT

@pytest.mark.reporting
def test_attach_json_with_allure(monkeypatch):
    captured = {}

    def fake_attach(body, name, attachment_type):
        captured["body"] = body
        captured["name"] = name
        captured["attachment_type"] = attachment_type

    monkeypatch.setattr(allure_tools.allure, "attach", fake_attach)

    attach_json("response", {"name": "John", "id": 10})

    assert json.loads(captured["body"]) == {"name": "John", "id": 10}
    assert captured["body"] == '{\n  "name": "John",\n  "id": 10\n}'
    assert captured["name"] == "response"
    assert captured["attachment_type"] == allure_tools.allure.attachment_type.JSON

@pytest.mark.reporting
def test_attach_text_without_allure(monkeypatch):
    monkeypatch.setattr(allure_tools, "allure", None)

    assert attach_text("response", "Hello") is None


@pytest.mark.reporting
def test_attach_json_without_allure(monkeypatch):
    monkeypatch.setattr(allure_tools, "allure", None)

    assert attach_json("response", {"name": "John", "id": 10}) is None

@pytest.mark.reporting
def test_step_without_allure(monkeypatch):
    monkeypatch.setattr(allure_tools, "allure", None)

    with step("test step"):
        value = 2 + 2

    assert value == 4

@pytest.mark.reporting
def test_step_with_allure(monkeypatch):
    captured = {}

    @contextmanager
    def fake_step(title):
        captured["title"] = title
        yield

    monkeypatch.setattr(allure_tools.allure, "step", fake_step)

    with step("Create user"):
        captured["executed"] = True

    assert captured["title"] == "Create user"
    assert captured["executed"] is True



@pytest.mark.parametrize(
    "level",
    [
        SeverityLevel.BLOCKER,
        SeverityLevel.CRITICAL,
        SeverityLevel.NORMAL,
        SeverityLevel.MINOR,
        SeverityLevel.TRIVIAL,
    ],
)
def test_severity_accepts_valid_levels(level):
    decorator = severity(level)

    assert callable(decorator)


@pytest.mark.parametrize(
    "value",
    [
        "blocker",
        "critical",
        "normal",
        "minor",
        "trivial",
        "SUPER_CRITICAL",
        "",
        None,
        123,
    ],
)
def test_severity_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="severity must be a SeverityLevel value"):
        severity(value)

@pytest.mark.parametrize(
    "value",
    [
        SeverityLevel.BLOCKER,
        SeverityLevel.CRITICAL, 
        SeverityLevel.NORMAL,
        SeverityLevel.MINOR,
        SeverityLevel.TRIVIAL,
    ],
)
def test_severity_passes_valid_values_to_allure(monkeypatch, value):

    captured = {}

    def fake_decorator(value):
        captured["value"] = value

        def decorator(fn):
            return fn

        return decorator

    monkeypatch.setattr(
        allure_tools.allure,
        "severity",
        fake_decorator,
    )

    def sample_test():
        return "OK"

    decorated_test = severity(value)(sample_test)

    assert captured["value"] == value.value
    assert decorated_test() == "OK"


@pytest.mark.reporting
def test_import_error_without_allure(monkeypatch):
    import builtins
    import importlib

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "allure":
            raise ImportError("Allure is unavailable")

        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    module = importlib.reload(allure_tools)

    assert module.allure is None

    monkeypatch.undo()
    importlib.reload(allure_tools)