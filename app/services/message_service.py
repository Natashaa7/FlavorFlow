from psycopg2.extras import RealDictCursor
from app.db.session import get_db_connection


def get_all_messages():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, full_name, email, subject, message, created_at
        FROM messages
        ORDER BY created_at DESC
    """)

    messages = cur.fetchall()

    cur.close()
    conn.close()
    return messages


def delete_message(message_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM messages WHERE id = %s",
        (message_id,)
    )

    conn.commit()
    cur.close()
    conn.close()
