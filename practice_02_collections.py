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

def main():
    print(len(TEST_CASES))

if __name__ == "__main__":
    main()