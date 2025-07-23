import psycopg2
from datetime import datetime
from utils import hash_datapoint

DB = {
    'dbname': 'finance',
    'user': 'postgres',
    'password': 'yourpass',
    'host': 'localhost'
}

METRICS = ['Revenue', 'Gross Profit', 'EBITDA']


def fetch_all_metrics(cur):
    cur.execute("""
        SELECT id, company_id, period_id, metric, value_type, frequency, value
        FROM financial_metrics
        WHERE metric = ANY(%s)
    """, (METRICS,))
    return cur.fetchall()


def calculate_variance(current, previous, calc_type):
    try:
        delta = current - previous
        pct = (delta / previous) * 100 if previous != 0 else None
    except ZeroDivisionError:
        pct = None
    return {
        "calculation_type": calc_type,
        "value": pct,
        "unit": "%",
        "note": f"{calc_type}: ({current} - {previous}) / {previous}",
        "corroboration_status": "pending"
    }


def insert_derived_metric(cur, base_metric, calculation_type, freq, company_id, period_id,
                          value, unit, source_ids, note, corroboration="pending"):
    cur.execute("""
        INSERT INTO derived_metrics (
            base_metric, calculation_type, frequency,
            company_id, period_id, calculated_value, unit,
            source_ids, calculation_note, corroboration_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        base_metric, calculation_type, freq,
        company_id, period_id, value, unit,
        source_ids, note, corroboration
    ))


def process_variances(cur, data):
    # Group by company, metric, frequency
    by_company = {}
    for row in data:
        k = (row[1], row[3], row[5])  # (company_id, metric, frequency)
        by_company.setdefault(k, []).append(row)

    for (company_id, metric, freq), entries in by_company.items():
        # Order by period_id
        entries = sorted(entries, key=lambda x: x[2])
        for i in range(1, len(entries)):
            curr = entries[i]
            prev = entries[i - 1]

            if curr[4] == 'actual' and prev[4] == 'actual':
                # MoM or QoQ
                result = calculate_variance(curr[6], prev[6], "Growth vs Prior Period")
                insert_derived_metric(
                    cur,
                    base_metric=metric,
                    calculation_type=result["calculation_type"],
                    freq=freq,
                    company_id=company_id,
                    period_id=curr[2],
                    value=result["value"],
                    unit=result["unit"],
                    source_ids=[curr[0], prev[0]],
                    note=result["note"]
                )

        # Budget vs Actual for same period
        for entry in entries:
            for compare in entries:
                if entry[2] == compare[2] and entry[4] == 'actual' and compare[4] == 'budget':
                    result = calculate_variance(entry[6], compare[6], "Variance vs Budget")
                    insert_derived_metric(
                        cur,
                        base_metric=metric,
                        calculation_type=result["calculation_type"],
                        freq=freq,
                        company_id=company_id,
                        period_id=entry[2],
                        value=result["value"],
                        unit=result["unit"],
                        source_ids=[entry[0], compare[0]],
                        note=result["note"]
                    )


def main():
    with psycopg2.connect(**DB) as conn:
        with conn.cursor() as cur:
            print("Fetching raw financial metrics...")
            data = fetch_all_metrics(cur)
            print("Calculating variances...")
            process_variances(cur, data)
            conn.commit()
            print("✅ Done: Derived metrics inserted.")


if __name__ == "__main__":
    main()
