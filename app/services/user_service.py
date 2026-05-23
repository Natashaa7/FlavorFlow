import bcrypt
from app.db.session import get_db_connection
from psycopg2.extras import RealDictCursor
from datetime import datetime


# =========================
# GET ALL USERS
# =========================
def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT id, name, email, username, phonenumber, dob, is_admin, last_login, created_at
            FROM users
            ORDER BY id DESC
        """)
        return cur.fetchall()

    finally:
        cur.close()
        conn.close()


# =========================
# ADD USER
# =========================
def add_user(data: dict):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Check duplicate email
        cur.execute("SELECT id FROM users WHERE email = %s", (data["email"],))
        if cur.fetchone():
            return {"success": False, "error": "email-exists"}

        # Check duplicate username
        cur.execute("SELECT id FROM users WHERE username = %s", (data["username"],))
        if cur.fetchone():
            return {"success": False, "error": "username-exists"}

        # Hash password
        hashed_password = bcrypt.hashpw(
            data["password"].encode("utf-8"),
            bcrypt.gensalt()
        ).decode()

        cur.execute("""
            INSERT INTO users (name, email, username, phonenumber, dob, password, is_admin)
            VALUES (%s, %s, %s, %s, %s, %s, FALSE)
        """, (
            data["name"],
            data["email"],
            data["username"],
            data["phonenumber"],
            data["dob"],
            hashed_password
        ))

        conn.commit()
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        cur.close()
        conn.close()


# =========================
# UPDATE USER
# =========================
def update_user(user_id: int, data: dict):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Check duplicate email on update (excluding this user)
        cur.execute(
            "SELECT id FROM users WHERE email = %s AND id != %s",
            (data.get("email"), user_id)
        )
        if cur.fetchone():
            return {"success": False, "error": "email-exists"}

        # Check duplicate username on update (excluding this user)
        cur.execute(
            "SELECT id FROM users WHERE username = %s AND id != %s",
            (data.get("username"), user_id)
        )
        if cur.fetchone():
            return {"success": False, "error": "username-exists"}

        fields = ["name=%s", "email=%s", "username=%s", "phonenumber=%s", "dob=%s"]
        values = [
            data.get("name"),
            data.get("email"),
            data.get("username"),
            data.get("phonenumber"),
            data.get("dob")
        ]

        # Optional password update
        if data.get("password"):
            hashed = bcrypt.hashpw(
                data["password"].encode("utf-8"),
                bcrypt.gensalt()
            ).decode()
            fields.append("password=%s")
            values.append(hashed)

        values.append(user_id)

        cur.execute(
            f"UPDATE users SET {', '.join(fields)} WHERE id = %s",
            values
        )
        conn.commit()
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        cur.close()
        conn.close()


# =========================
# DELETE USER
# =========================
def delete_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        cur.close()
        conn.close()


# =========================
# GET SINGLE USER
# =========================
def get_user_by_id(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()

    finally:
        cur.close()
        conn.close()