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

def tags_frequency(cases) -> dict[str, int]:
    res: dict[str, int] = {}
    for c in cases:
        for t in c["tags"]:
            res[t] = res.get(t, 0) + 1
    return res

weight_priority = {"critical": 4,
                   "high": 3,
                   "medium": 2,
                   "low": 1}

weight_tags = {"smoke": 2,
               "flaky": -2}

def select_risk_based(cases, budget: int) -> list[str]:
    import heapq
    heap = []
    for c in cases:
        if not c["automated"]:
            continue
        res = weight_priority[c["priority"]]
        for t in weight_tags:
            if t in c["tags"]:
                res += weight_tags[t]
        heapq.heappush(heap, (res, -int(c["id"][2:]), c["id"]))
        if len(heap) > budget:
            heapq.heappop(heap)
    res = list(heap)
    res.sort(key=lambda x: (-x[0], -x[1]))
    return [id for _, _, id in res]

def explain_scores(cases) -> list[tuple[str, int]]:
    heap = []
    for c in cases:
        if not c["automated"]:
            continue
        res = weight_priority[c["priority"]]
        for t in weight_tags:
            if t in c["tags"]:
                res += weight_tags[t]
        heap.append((c["id"], res))
    heap.sort(key=lambda x: (-x[1], int(x[0][2:])))
    return heap

def feature_stats(cases) -> dict[str, dict]:
    d: dict[str, dict] = {}
    for c in cases:
        d.setdefault(c["feature"], {
                                    "total": 0,
                                    "automated": 0,
                                    "manual": 0,
                                    "platforms": set()
                                })
        d[c["feature"]]["total"] += 1
        d[c["feature"]]["automated"] += 1 if c["automated"] else 0
        d[c["feature"]]["manual"] += 1 if not c["automated"] else 0
        d[c["feature"]]["platforms"].add(c["platform"])
    return d

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

    freq = tags_frequency(TEST_CASES)
    assert freq["smoke"] >= 3
    assert freq["device"] >= 4
    assert freq["auth"] == 3
    assert freq["cloud"] == 3
    assert freq["flaky"] == 1
    assert freq["ui"] == 1
    print("tags_frequency OK")

    scores = explain_scores(TEST_CASES)
    assert ("TC001", 6) in scores
    assert ("TC008", 1) in scores
    # manual нет в scores:
    assert all(x[0] not in {"TC003", "TC005", "TC009"} for x in scores)
    top5 = select_risk_based(TEST_CASES, 5)
    assert len(top5) == 5
    assert "TC003" not in top5 and "TC005" not in top5 and "TC009" not in top5
    print("select_risk_based OK")

    crit_ids = [c["id"] for c in TEST_CASES if c["priority"] == "critical"]
    feat_count = {
                    feature: sum(1 for c in TEST_CASES if c["feature"] == feature)
                                for feature in {c["feature"] for c in TEST_CASES}
                                } 
    crit_platforms = {c["platform"] for c in TEST_CASES if c["priority"] == "critical"}

    assert set(crit_ids) == {"TC001", "TC004", "TC007", "TC010"}
    assert feat_count["login"] == 4
    assert feat_count["dfu"] == 3
    assert "windows" in crit_platforms and "macos" in crit_platforms
    stats = feature_stats(TEST_CASES)
    assert stats["login"]["total"] == 4
    assert stats["login"]["automated"] == 3
    assert stats["login"]["manual"] == 1
    assert stats["bluetooth"]["platforms"] == {"android", "ios"}
    print("feature_stats OK")

if __name__ == "__main__":
    main()