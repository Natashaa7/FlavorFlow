import uuid
import shutil
from typing import Optional
from psycopg2.extras import RealDictCursor
from app.db.session import get_db_connection


# ---------------------------
# ROLE CHECK
# ---------------------------
def get_user_role(cur, user_id: int):
    cur.execute("SELECT is_admin FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    return user["is_admin"] if user else False


# ---------------------------
# GET RECIPES
# ---------------------------
def get_user_recipes(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, title, description, image_path, file_path, cook_time, difficulty, created_at
        FROM recipe
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (user_id,))

    recipes = cur.fetchall()
    cur.close()
    conn.close()

    return recipes


# ---------------------------
# ADD RECIPE
# ---------------------------
def add_recipe_db(data, image, file, user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        image_name = f"{uuid.uuid4()}_{image.filename}"
        file_name = f"{uuid.uuid4()}_{file.filename}"

        image_path = f"uploads/images/{image_name}"
        file_path = f"uploads/files/{file_name}"

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        cur.execute("""
            INSERT INTO recipe
            (title, description, image_path, file_path, cook_time, difficulty, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data["title"], data["description"],
            "/" + image_path, "/" + file_path,
            data["cook_time"], data["difficulty"], user_id
        ))

        conn.commit()
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        cur.close()
        conn.close()


# ---------------------------
# UPDATE RECIPE
# ---------------------------
def update_recipe_db(id, data, image, file, user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        fields = ["title=%s", "description=%s", "cook_time=%s", "difficulty=%s"]
        values = [
            data["title"], data["description"],
            data["cook_time"], data["difficulty"]
        ]

        if image:
            image_name = f"{uuid.uuid4()}_{image.filename}"
            image_path = f"uploads/images/{image_name}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            fields.append("image_path=%s")
            values.append("/" + image_path)

        if file:
            file_name = f"{uuid.uuid4()}_{file.filename}"
            file_path = f"uploads/files/{file_name}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            fields.append("file_path=%s")
            values.append("/" + file_path)

        values.extend([id, user_id])

        cur.execute(f"""
            UPDATE recipe
            SET {', '.join(fields)}
            WHERE id=%s AND user_id=%s
        """, values)

        conn.commit()
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        cur.close()
        conn.close()


# ---------------------------
# DELETE RECIPE
# ---------------------------
def delete_recipe_db(id, user_id, is_admin):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if is_admin:
            cur.execute("DELETE FROM recipe WHERE id=%s", (id,))
        else:
            cur.execute("DELETE FROM recipe WHERE id=%s AND user_id=%s", (id, user_id))

        # ✅ IMPORTANT FIX
        if cur.rowcount == 0:
            return {"success": False, "error": "Recipe not found or unauthorized"}

        conn.commit()
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

    finally:
        cur.close()
        conn.close()


# view recipe details (for both user and public views)
def get_recipe_by_id(recipe_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # increase views
        cur.execute("""
            UPDATE recipe
            SET views = views + 1
            WHERE id = %s
        """, (recipe_id,))

        # fetch recipe
        cur.execute("""
            SELECT id, title, description, file_path, views
            FROM recipe
            WHERE id = %s
        """, (recipe_id,))

        recipe = cur.fetchone()
        conn.commit()

        return recipe

    finally:
        cur.close()
        conn.close()