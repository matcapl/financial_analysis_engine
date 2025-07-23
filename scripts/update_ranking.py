import psycopg2
from datetime import datetime

DB = {
    'dbname': 'finance',
    'user': 'postgres',
    'password': 'yourpass',
    'host': 'localhost'
}


def fetch_active_questions(cur):
    cur.execute("""
        SELECT id, rank_score, rank_position
        FROM live_questions
        WHERE status = 'active'
        ORDER BY rank_score DESC NULLS LAST
    """)
    return cur.fetchall()


def update_rank(cur, question_id, old_position, new_position):
    cur.execute("""
        UPDATE live_questions
        SET rank_position = %s, last_updated = NOW()
        WHERE id = %s
    """, (new_position, question_id))

    cur.execute("""
        INSERT INTO question_logs (
            live_question_id, change_type, changed_by,
            old_value, new_value, change_note
        ) VALUES (%s, 'rank_updated', 'system', %s, %s, %s)
    """, (
        question_id,
        old_position,
        new_position,
        f"Rank position updated from {old_position} to {new_position}"
    ))


def main():
    with psycopg2.connect(**DB) as conn:
        with conn.cursor() as cur:
            active_questions = fetch_active_questions(cur)

            print("🧮 Re-ranking active questions...")

            for i, (qid, score, old_rank) in enumerate(active_questions, start=1):
                if old_rank != i:
                    update_rank(cur, qid, old_rank, i)

            conn.commit()
            print(f"✅ Ranking updated: {len(active_questions)} questions reassigned")


if __name__ == "__main__":
    main()
