from datetime import datetime, timedelta
import random
from psycopg2.extras import RealDictCursor
from app.db.session import get_db_connection


def create_reset_code(email: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return None

    code = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=10)

    cur.execute("""
        UPDATE users
        SET reset_code=%s,
            reset_code_expiry=%s
        WHERE email=%s
    """, (code, expiry, email))

    conn.commit()
    cur.close()
    conn.close()

    return code
