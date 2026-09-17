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
    return data

def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Not path to file")
    try:
        print(len(load_payload(sys.argv[1])))
    except InputFileError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
