import sys
import json
from pathlib import Path

class InputFileError(Exception):
    def __init__(self, path: Path):
        self.path = path
        super().__init__(f"Input file not found: {path}")

class PayloadError(Exception):
    def __init__(self, path: Path, message: str = ''):
        self.path = path
        super().__init__(f"Invalid JSON in {path}" if not message else message)

class EnvError(Exception):
    pass

def load_payload(path: str) -> list:
    path = Path(path)
    if not path.exists():
        raise InputFileError(path) 
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise PayloadError(path) from e
    if not isinstance(data, list):
        raise PayloadError(path, "Invalid payload structure")
    required = {"id", "status", "latency_ms", "endpoint"} 
    for d in data:
        if not isinstance(d, dict):
            raise PayloadError(path, "Invalid payload structure")
        if not required.issubset(d.keys()):
            raise PayloadError(path, "Invalid payload structure")

    return data

def analyze(data: list) -> dict:
    total = len(data)
    success = sum(1 for d in data if 200 <= d["status"] <= 299)
    errors = sum(1 for d in data if d["status"] >= 400)
    avg_latency_ms = round(sum(d["latency_ms"] for d in data) / total, 1)
    endpoint: dict[str, int] = {}
    for d in data:
        if d["status"] >= 400:
            endpoint[d["endpoint"]] = endpoint.get(d["endpoint"], 0) + 1
    worst_endpoint = max(endpoint, key=endpoint.get)
    return {"total": total,
            "success": success,
            "errors": errors,
            "avg_latency_ms": avg_latency_ms,
            "worst_endpoint": worst_endpoint}
    

def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Not path to file")
    try:
        print(analyze(load_payload(sys.argv[1])))
    except (InputFileError, PayloadError) as e:
        sys.exit(str(e))

if __name__ == "__main__":
    main()
