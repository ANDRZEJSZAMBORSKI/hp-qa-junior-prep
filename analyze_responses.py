import sys
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

class InputFileError(Exception):
    def __init__(self, path: Path):
        self.path = path
        super().__init__(f"Input file not found: {path}")

class PayloadError(Exception):
    def __init__(self, path: Path, message: str = ''):
        self.path = path
        super().__init__(f"Invalid JSON in {path}" if not message else message)

class EnvError(Exception):
    def __init__(self, message: str = ''):
        super().__init__(message)

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
    
def print_report_Console(stats: dict) -> None:
    console = Console()
    console.print(stats)

def print_report_Table(stats: dict) -> None:
    console = Console()

    table = Table()
    table.add_column("Metric")
    table.add_column("Value")

    for key, value in stats.items():
        table.add_row(key, str(value))

    console.print(table)

def self_check(s: str) -> str:
    path = Path(__file__).resolve().parent / s
    if not path.exists():
        raise EnvError(f"{path} not found")
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            l = line.strip()
            if l.startswith("rich=="):
                _, v = l.split('==')
                if v: 
                    return l
                else:
                    raise EnvError(f"rich== not found in {path}")
    raise EnvError(f"rich== not found in {path}")

def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Not path to file")
    try:
        if sys.argv[1] == "--self-check":
            if self_check("requirements.txt"):
                print("self-check OK")
            return
        data = load_payload(sys.argv[1])
        stats = analyze(data)
        print_report_Table(stats)
    except (InputFileError, PayloadError, EnvError) as e:
        sys.exit(str(e))

if __name__ == "__main__":
    main()
