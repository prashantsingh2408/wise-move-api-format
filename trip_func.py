import json
from typing import List, Dict, Any, Optional
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def load_json_file(filename: str) -> Optional[Dict[str, Any]]:
    file_path = DATA_DIR / filename
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {file_path}.")
    return None

def load_trip() -> Optional[Dict[str, Any]]:
    return load_json_file("trips.json")

def load_safety_trip() -> Optional[Dict[str, Any]]:
    return load_json_file("safety_trips.json")

def load_safety_reports() -> Optional[Dict[str, Any]]:
    return load_json_file("safety_reports.json")

def get_trip_by_id(trip_id: str) -> Optional[Dict[str, Any]]:
    trips = load_trip()
    if not trips:
        return None
    return trips.get(trip_id)
