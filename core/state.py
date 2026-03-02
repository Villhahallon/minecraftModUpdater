import json
from pathlib import Path

def load_state(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}

def save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, indent=2))