import hashlib
import json
from datetime import datetime

def hash_datapoint(row):
    key = f"{row['company_id']}-{row['period_id']}-{row['metric']}-{row['value_type']}-{row['frequency']}"
    return hashlib.sha256(key.encode()).hexdigest()

def find_existing_datapoint(cur, row, hashed):
    cur.execute("""
        SELECT id FROM financial_metrics
        WHERE company_id = %s AND period_id = %s
        AND metric = %s AND value_type = %s AND frequency = %s
    """, (
        row['company_id'], row['period_id'],
        row['metric'], row['value_type'], row['frequency']
    ))
    return cur.fetchone()

def log_event(message, source_file):
    log_path = f"logs/ingest_log_{datetime.today().date()}.json"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "source": source_file,
        "event": message
    }
    try:
        with open(log_path, "r") as f:
            log = json.load(f)
    except FileNotFoundError:
        log = []

    log.append(entry)

    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
