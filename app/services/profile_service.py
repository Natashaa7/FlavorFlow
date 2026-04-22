import bcrypt
from psycopg2.extras import RealDictCursor
from app.db.session import get_db_connection

def get_user_role(cur, user_id):
    cur.execute("SELECT is_admin FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    return user["is_admin"] if user else False


def get_profile_data(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        is_admin = get_user_role(cur, user_id)

        # recipes
        cur.execute("SELECT COUNT(*) FROM recipe WHERE user_id=%s", (user_id,))
        recipes_result = cur.fetchone()
        recipes_shared = recipes_result["count"] if recipes_result else 0

        # favorites
        cur.execute("SELECT COUNT(*) FROM favorite WHERE user_id=%s", (user_id,))
        favorites_result = cur.fetchone()
        favorites_count = favorites_result["count"] if favorites_result else 0

        # MOST LIKED
        cur.execute("""
            SELECT r.title, COUNT(f.id) AS like_count
            FROM recipe r
            LEFT JOIN favorite f ON r.id = f.recipe_id
            WHERE r.user_id=%s
            GROUP BY r.id, r.title
            ORDER BY like_count DESC
            LIMIT 1
        """, (user_id,))
        most_liked = cur.fetchone()

        # MOST VIEWED
        cur.execute("""
            SELECT title, views
            FROM recipe
            WHERE user_id=%s
            ORDER BY views DESC
            LIMIT 1
        """, (user_id,))
        most_viewed = cur.fetchone()

        # USER
        cur.execute("""
            SELECT name, email, username, phonenumber, dob, created_at, profile_image
            FROM users WHERE id=%s
        """, (user_id,))
        user = cur.fetchone()

        return {
            "is_admin": is_admin,
            "recipes_shared": recipes_shared,
            "favorites_count": favorites_count,

            # FIXED STRUCTURE FOR TEMPLATE
            "most_liked_recipe_title": most_liked["title"] if most_liked else None,
            "most_liked_recipe_count": most_liked["like_count"] if most_liked else 0,

            "most_viewed_title": most_viewed["title"] if most_viewed else None,
            "most_viewed_views": most_viewed["views"] if most_viewed else 0,

            "user": user
        }

    finally:
        cur.close()
        conn.close()



def update_profile(user_id, data):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    errors = []

    try:
        # Get user
        cur.execute("SELECT password FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()

        if not user:
            return {"success": False, "errors": ["User not found"]}

        stored_password = user["password"]

        # -------------------------
        # DUPLICATE CHECKS (simple)
        # -------------------------
        for field in ["email", "phonenumber", "username"]:
            if data.get(field):
                cur.execute(
                    f"SELECT 1 FROM users WHERE {field}=%s AND id != %s",
                    (data[field], user_id)
                )
                if cur.fetchone():
                    errors.append(f"{field.capitalize()} already exists")

        # -------------------------
        # PASSWORD CHECK
        # -------------------------
        if data.get("password"):
            if not data.get("current_password"):
                errors.append("Current password required")
            elif not bcrypt.checkpw(
                data["current_password"].encode(),
                stored_password.encode()
            ):
                errors.append("Wrong current password")

            if data["password"] != data.get("confirm_password"):
                errors.append("Passwords do not match")

        # -------------------------
        # RETURN ERRORS
        # -------------------------
        if errors:
            return {"success": False, "errors": errors}

        # -------------------------
        # HASH PASSWORD (if needed)
        # -------------------------
        hashed_password = stored_password
        if data.get("password"):
            hashed_password = bcrypt.hashpw(
                data["password"].encode(), bcrypt.gensalt()
            ).decode()

        # -------------------------
        # UPDATE
        # -------------------------
        cur.execute("""
            UPDATE users
            SET name=%s, username=%s, email=%s,
                phonenumber=%s, dob=%s, password=%s
            WHERE id=%s
        """, (
            data["name"], data["username"], data["email"],
            data["phonenumber"], data["dob"],
            hashed_password, user_id
        ))

        conn.commit()

        return {"success": True}

    finally:
        cur.close()
        conn.close()



def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        return True
    finally:
        cur.close()
        conn.close()
