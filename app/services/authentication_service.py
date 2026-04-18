import bcrypt
from datetime import datetime
from psycopg2.extras import RealDictCursor
from psycopg2 import errors
from app.db.session import get_db_connection


def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, email, username, phonenumber FROM users;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users


def create_user(data):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    hashed_password = bcrypt.hashpw(
        data["password"].encode(), bcrypt.gensalt()
    ).decode()

    try:
        cur.execute("""
            INSERT INTO users (name, email, username, phonenumber, password, is_admin, oauth_provider)
            VALUES (%s, %s, %s, %s, %s, FALSE, %s)
            RETURNING id
        """, (
            data["name"], data["email"], data["username"],
            data["phonenumber"], hashed_password, "local"
        ))

        row = cur.fetchone()
        if row is None:
            conn.rollback()
            return {"success": False, "error": "Failed to create user"}

        user_id = row["id"]

        cur.execute(
            "UPDATE users SET last_login=%s WHERE id=%s",
            (datetime.utcnow(), user_id)
        )

        conn.commit()
        return {"success": True, "user_id": user_id}

    except errors.UniqueViolation as e:
        conn.rollback()
        if "email" in str(e):
            return {"success": False, "error": "Email already registered"}
        elif "username" in str(e):
            return {"success": False, "error": "Username already taken"}
        return {"success": False, "error": "User already exists"}

    finally:
        cur.close()
        conn.close()


def authenticate_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user or not user.get("password"):
        return None

    stored_password = user["password"]

    if not bcrypt.checkpw(password.encode(), stored_password.encode()):
        return None

    return user


def update_last_login(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET last_login=%s WHERE id=%s",
        (datetime.utcnow(), user_id)
    )
    conn.commit()
    cur.close()
    conn.close()
