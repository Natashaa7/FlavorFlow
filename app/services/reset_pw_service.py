import bcrypt
from datetime import datetime
from psycopg2.extras import RealDictCursor
from app.db.session import get_db_connection
from app.utils.validation import validate_password


def verify_reset_code(email, code):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return None, "User not found"

    if user["reset_code"] != code or datetime.utcnow() > user["reset_code_expiry"]:
        return None, "Invalid or expired reset code"

    return user, None


def reset_user_password(email, new_password):
    conn = get_db_connection()
    cur = conn.cursor()

    validate_password(new_password)

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

    cur.execute("""
        UPDATE users
        SET password=%s,
            reset_code=NULL,
            reset_code_expiry=NULL
        WHERE email=%s
    """, (hashed, email))

    conn.commit()
    cur.close()
    conn.close()
