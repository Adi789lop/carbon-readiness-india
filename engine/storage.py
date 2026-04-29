"""
Storage engine — JSON file-based supplier data persistence
Defensive against missing files, corrupted data, encoding issues
"""

import json
import os
import re
from datetime import datetime

DB_FILE = "supplier_data.json"


def make_id(company_name, pan):
    """Generate a unique Supplier ID from company name + PAN"""
    pan_clean = (pan or "NOPAN").upper().strip()
    name_clean = re.sub(r'[^A-Z0-9]', '', (company_name or "UNKNOWN").upper())[:20]
    timestamp = datetime.now().strftime("%y%m%d")
    return f"SUP-{pan_clean}-{name_clean}-{timestamp}"


def load_all():
    """Load all supplier records — returns empty dict if file missing or corrupted"""
    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Handle empty file
        if not content:
            return {}

        # Handle BOM if present (UTF-8 BOM = \ufeff)
        if content.startswith("\ufeff"):
            content = content[1:]

        data = json.loads(content)
        if not isinstance(data, dict):
            return {}
        return data

    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        # File is corrupted — backup and reset
        try:
            backup_name = f"supplier_data_corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json.bak"
            os.rename(DB_FILE, backup_name)
        except Exception:
            pass
        return {}

    except Exception:
        return {}


def load_one(sid):
    """Retrieve a single supplier record by Supplier ID"""
    all_data = load_all()
    return all_data.get(sid)


def save(sid, record):
    """Save or update a supplier record"""
    all_data = load_all()

    # Add timestamp
    record['timestamp'] = datetime.now().isoformat()
    record['sid'] = sid

    all_data[sid] = record

    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving: {e}")
        return False


def delete_one(sid):
    """Delete a single supplier record"""
    all_data = load_all()
    if sid in all_data:
        del all_data[sid]
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        return True
    return False


def delete_all():
    """Reset the entire database"""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return True
    except Exception:
        return False