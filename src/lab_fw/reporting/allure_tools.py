from contextlib import contextmanager
from functools import wraps
from enum import StrEnum
import json
try:
    import allure
except ImportError:
    allure = None

class SeverityLevel(StrEnum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    NORMAL = "normal"
    MINOR = "minor"
    TRIVIAL = "trivial"

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

def decor_allure(dec_allure: str, value: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        
        if allure is None:
            return wrapper
        
        dec_func = getattr(allure, dec_allure)
        return dec_func(value)(wrapper)
    
    return decorator

def epic(value):
    return decor_allure("epic", value)

def feature(value):
    return decor_allure("feature", value)

def severity(value: SeverityLevel):
    if not isinstance(value, SeverityLevel):
        raise ValueError(
            "severity must be a SeverityLevel value"
        )
    return decor_allure("severity", value.value)

def title(value):
    return decor_allure("title", value)

def description(value):
    return decor_allure("description", value)