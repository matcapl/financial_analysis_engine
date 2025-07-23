import psycopg2
from datetime import datetime

DB = {
    'dbname': 'finance',
    'user': 'postgres',
    'password': 'yourpass',
    'host': 'localhost'
}

# Threshold for flagging a question (score = |% change| × weight)
SCORE_THRESHOLD = 0.5


def fetch_metric_weights(cur):
    cur.execute("""
        SELECT metric, default_weight
        FROM metric_weights
    """)
    return {row[0]: float(row[1]) for row in cur.fetchall()}


def fetch_derived_metrics(cur):
    cur.execute("""
        SELECT id, base_metric, calculation_type, company_id,
               period_id, calculated_value
        FROM derived_metrics
    """)
    return cur.fetchall()


def question_exists(cur, derived_metric_id):
    cur.execute("""
        SELECT id FROM live_questions
        WHERE derived_metric_id = %s AND status = 'active'
    """, (derived_metric_id,))
    return cur.fetchone() is not None


def build_question(metric, calc_type, value):
    direction = "increased" if value > 0 else "decreased" if value < 0 else "stayed flat"
    return f"Why did {metric} {direction} by {round(abs(value), 2)}% {calc_type.lower()}?"


def insert_question(cur, derived_metric_id, metric, calc_type, value, weight):
    direction = "increase" if value > 0 else "decline" if value < 0 else "flat"
    magnitude = abs(value)
    score = round(magnitude * weight, 4)

    scorecard = {
        "magnitude": magnitude,
        "weight": weight,
        "score": score,
        "direction": direction
    }

    question_text = build_question(metric, calc_type, value)

    cur.execute("""
        INSERT INTO live_questions (
            derived_metric_id, template_id, weight,
            scorecard, rank_score, rank_position
        ) VALUES (%s, NULL, %s, %s::jsonb, %s, NULL)
    """, (
        derived_metric_id, weight,
        str(scorecard).replace("'", '"'), score
    ))

    cur.execute("""
        INSERT INTO question_logs (
            live_question_id, change_type, changed_by,
            old_value, new_value, change_note
        ) VALUES (
            currval('live_questions_id_seq'), 'question_created', 'system',
            NULL, %s, %s
        )
    """, (
        str(scorecard).replace("'", '"'),
        f"Generated from {metric} {calc_type} ({direction})"
    ))

    print(f"✅ Question raised: {question_text}")


def main():
    with psycopg2.connect(**DB) as conn:
        with conn.cursor() as cur:
            weights = fetch_metric_weights(cur)
            derived = fetch_derived_metrics(cur)

            created = 0
            for row in derived:
                derived_id, metric, calc_type, company, period, value = row
                if value is None:
                    continue
                weight = weights.get(metric, 0.5)
                score = abs(value) * weight

                if score >= SCORE_THRESHOLD and not question_exists(cur, derived_id):
                    insert_question(cur, derived_id, metric, calc_type, value, weight)
                    created += 1

            conn.commit()
            print(f"\n🎯 Total questions created: {created}")


if __name__ == "__main__":
    main()
