from datetime import datetime
from psycopg2.extras import RealDictCursor
from app.db.session import get_db_connection


def get_or_create_google_user(user_info: dict):
    email = user_info["email"]
    name = user_info["name"]
    username = email.split("@")[0]

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Check existing user
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user:
        cur.execute("""
            INSERT INTO users (name, email, username, password, is_admin, oauth_provider)
            VALUES (%s, %s, %s, NULL, FALSE, %s)
            RETURNING id, is_admin
        """, (name, email, username, "google"))

        user = cur.fetchone()
        user_id = user["id"]
        is_admin = False
        conn.commit()

    else:
        user_id = user["id"]
        is_admin = user["is_admin"]

    # update last login
    cur.execute(
        "UPDATE users SET last_login=%s WHERE id=%s",
        (datetime.utcnow(), user_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "id": user_id,
        "is_admin": is_admin
    }
