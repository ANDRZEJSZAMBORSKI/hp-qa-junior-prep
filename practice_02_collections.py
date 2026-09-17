TEST_CASES = [
  {"id": "TC001", "feature": "login",   "priority": "critical", "platform": "windows", "automated": True,  "tags": ["smoke", "auth"]},
  {"id": "TC002", "feature": "login",   "priority": "high",     "platform": "macos",   "automated": True,  "tags": ["auth"]},
  {"id": "TC003", "feature": "login",   "priority": "low",      "platform": "windows", "automated": False, "tags": ["ui"]},
  {"id": "TC004", "feature": "dfu",     "priority": "critical", "platform": "windows", "automated": True,  "tags": ["device", "smoke"]},
  {"id": "TC005", "feature": "dfu",     "priority": "high",     "platform": "ios",     "automated": False, "tags": ["device"]},
  {"id": "TC006", "feature": "inventory","priority": "medium",  "platform": "android", "automated": True,  "tags": ["cloud"]},
  {"id": "TC007", "feature": "inventory","priority": "critical","platform": "windows", "automated": True,  "tags": ["cloud", "smoke"]},
  {"id": "TC008", "feature": "bluetooth","priority": "high",   "platform": "android", "automated": True,  "tags": ["device", "flaky"]},
  {"id": "TC009", "feature": "bluetooth","priority": "medium", "platform": "ios",     "automated": False, "tags": ["device"]},
  {"id": "TC010", "feature": "dfu",     "priority": "critical", "platform": "macos",   "automated": True,  "tags": ["device"]},
  {"id": "TC011", "feature": "login",   "priority": "high",     "platform": "windows", "automated": True,  "tags": ["auth", "smoke"]},
  {"id": "TC012", "feature": "inventory","priority": "low",     "platform": "linux",   "automated": True,  "tags": ["cloud"]},
]

requested = {"id", "feature", "priority", "platform", "automated", "tags"}

def index_by_id(cases) -> dict[str, dict]:    
    res: dict[str, dict] = {}
    for c in cases:
        if not requested.issubset(c.keys()):
            raise ValueError("Invalid payload structure")
        if c["id"] in res: 
            raise ValueError(f"Duplicate id: {c['id']}")
        res[c["id"]] = c
    return res

def filter_cases(cases: list[dict], **kwargs) -> list[dict]:
    res: list[dict] = []
    for key in kwargs:
        if key not in requested and key != 'priority_in':
            raise ValueError(f"Invalid field name: {key}")
    for c in cases:
        if 'priority_in' not in kwargs:
            if all(a == b for a, b in [(c[key], kwargs[key]) for key in kwargs]):
                res.append(c)
        else:
            if c["priority"] in kwargs["priority_in"]:
                tmp = [a == b for a, b in [(c[key], kwargs[key]) for key in kwargs if key != "priority_in"]]
                if all(tmp):
                    res.append(c)
    return res

def unique_platforms(cases) -> set[str]:
    return {c["platform"] for c in cases}

def tags_union(cases) -> set[str]:
    result = set()
    for c in cases:
        result.update(c["tags"])
    return result

def main():
    print(len(TEST_CASES))

    idx = index_by_id(TEST_CASES)
    assert len(idx) == 12
    assert idx["TC001"]["feature"] == "login"
    assert idx["TC001"]["priority"] == "critical"
    print("index_by_id OK")

    # 1. Фильтр по одному полю
    result = filter_cases(TEST_CASES, feature="login")
    assert len(result) == 4
    assert {c["id"] for c in result} == {"TC001", "TC002", "TC003", "TC011"}

    # 2. Фильтр по нескольким полям
    result = filter_cases(TEST_CASES, feature="login", platform="windows")
    assert len(result) == 3
    assert {c["id"] for c in result} == {"TC001", "TC003", "TC011"}

    # 3. Фильтр по automated
    result = filter_cases(TEST_CASES, automated=True)
    assert len(result) == 9

    # 4. priority_in
    result = filter_cases(TEST_CASES, priority_in={"critical", "high"})
    assert len(result) == 8
    assert {c["id"] for c in result} == {
        "TC001", "TC002", "TC004", "TC005",
        "TC007", "TC008", "TC010", "TC011"
    }

    # 5. priority_in + другое поле
    result = filter_cases(
        TEST_CASES,
        priority_in={"critical", "high"},
        feature="dfu"
    )
    assert len(result) == 3
    assert {c["id"] for c in result} == {"TC004", "TC005", "TC010"}

    # 6. Несколько обычных полей + priority_in
    result = filter_cases(
        TEST_CASES,
        priority_in={"critical", "high"},
        platform="windows",
        automated=True
    )
    assert len(result) == 4
    assert {c["id"] for c in result} == {"TC001", "TC004", "TC007", "TC011"}

    # 7. Нет совпадений
    result = filter_cases(TEST_CASES, feature="login", platform="linux")
    assert result == []

    # 8. Неверное имя поля
    try:
        filter_cases(TEST_CASES, wrong_field="test")
        assert False
    except ValueError:
        pass

    print("filter_cases OK")

    platforms = unique_platforms(TEST_CASES)
    assert platforms == {"windows", "macos", "ios", "android", "linux"}
    print("unique_platforms OK")

    tags = tags_union(TEST_CASES)
    assert tags == {"smoke", "auth", "ui", "device", "cloud", "flaky"}
    print("tags_union OK")

if __name__ == "__main__":
    main()