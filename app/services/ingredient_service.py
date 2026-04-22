from app.db.session import get_db_connection
from psycopg2.extras import RealDictCursor


# -------------------------
# CREATE
# -------------------------
def create_ingredient(name, category, usage_count):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        INSERT INTO ingredients (name, category, usage_count)
        VALUES (%s, %s, %s)
        RETURNING *
    """, (name, category, usage_count))

    result = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()
    return result


# -------------------------
# READ ALL
# -------------------------
def get_all_ingredients():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM ingredients ORDER BY id DESC")
    result = cur.fetchall()

    cur.close()
    conn.close()
    return result


# -------------------------
# READ ONE
# -------------------------
def get_ingredient_by_id(ingredient_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM ingredients WHERE id=%s", (ingredient_id,))
    result = cur.fetchone()

    cur.close()
    conn.close()
    return result


# -------------------------
# UPDATE
# -------------------------
def update_ingredient(ingredient_id, name, category, usage_count):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        UPDATE ingredients
        SET name=%s, category=%s, usage_count=%s
        WHERE id=%s
        RETURNING *
    """, (name, category, usage_count, ingredient_id))

    result = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()
    return result


# -------------------------
# DELETE
# -------------------------
def delete_ingredient(ingredient_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("DELETE FROM ingredients WHERE id=%s RETURNING id", (ingredient_id,))
    result = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return result
