import json
import os
import hashlib
from datetime import datetime

FILE = 'supplier_data.json'

def make_id(name: str, pan: str) -> str:
    raw = f'{name.lower().strip()}{pan.upper().strip()}'
    return hashlib.md5(raw.encode()).hexdigest()[:8].upper()

def save(sid: str, data: dict):
    all_d = load_all()
    all_d[sid] = {**data, 'ts': datetime.now().isoformat()}
    with open(FILE, 'w') as f:
        json.dump(all_d, f, indent=2)

def load_all() -> dict:
    if not os.path.exists(FILE):
        return {}
    with open(FILE) as f:
        return json.load(f)

def load_one(sid: str) -> dict:
    return load_all().get(sid, {})