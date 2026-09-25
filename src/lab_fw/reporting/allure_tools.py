from contextlib import contextmanager
import json
try:
    import allure
except ImportError:
    allure = None

@contextmanager
def step(title):
    if allure is None:
        yield
    else:
        with allure.step(title):
            yield

def attach_text(name, body):
    if allure is None:
        return

    allure.attach(
        body,
        name=name,
        attachment_type=allure.attachment_type.TEXT,
    )

def attach_json(name, data):
    if allure is None:
        return

    body = json.dumps(data, ensure_ascii=False, indent=2)

    allure.attach(
        body,
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )