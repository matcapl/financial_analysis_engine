import pandas as pd
import psycopg2
from datetime import datetime
import json
from utils import hash_datapoint, find_existing_datapoint, log_event

DB = {
    'dbname': 'finance',
    'user': 'postgres',
    'password': 'yourpass',
    'host': 'localhost'
}

SOURCE_FILE = 'data/boardpack_jun2025.xlsx'
SOURCE_PAGE = 1  # optional if coming from table or sheet

def parse_financials(xlsx_path):
    df = pd.read_excel(xlsx_path)
    return df  # expects standardised template from earlier

def ingest_row(row, cur):
    hashed = hash_datapoint(row)

    existing_id = find_existing_datapoint(cur, row, hashed)
    if existing_id:
        # Insert source reference to corroboration table
        cur.execute("""
            INSERT INTO datapoint_sources (datapoint_hash, source_file, source_page)
            VALUES (%s, %s, %s)
        """, (hashed, row['source_file'], row.get('source_page', None)))
        log_event(f"Corroborated datapoint {hashed}", row['source_file'])
    else:
        # Insert raw datapoint
        cur.execute("""
            INSERT INTO financial_metrics (
                company_id, period_id, metric, value_type, frequency,
                value, currency, source_file, source_page, cell_reference,
                source_type, calculation_note
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['company_id'], row['period_id'], row['metric'], row['value_type'],
            row['frequency'], row['value'], row['currency'],
            row['source_file'], row['source_page'], row['cell_reference'],
            row['source_type'], row['calculation_note']
        ))
        log_event(f"Inserted new datapoint {hashed}", row['source_file'])

def main():
    df = parse_financials(SOURCE_FILE)

    with psycopg2.connect(**DB) as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                ingest_row(row, cur)
        conn.commit()

    log_event(f"Ingestion complete: {SOURCE_FILE}", SOURCE_FILE)

if __name__ == "__main__":
    main()
