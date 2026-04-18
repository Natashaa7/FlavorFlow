from app.db.session import get_db_connection


def get_all_recipes(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT r.id, r.title, r.description, r.cook_time, r.difficulty,
               r.image_path, r.views, u.username,
               CASE WHEN f.id IS NOT NULL THEN TRUE ELSE FALSE END AS is_favorited
        FROM recipe r
        JOIN users u ON r.user_id = u.id
        LEFT JOIN favorite f
        ON r.id = f.recipe_id AND f.user_id = %s
        ORDER BY r.created_at DESC
    """, (user_id,))

    recipes = cur.fetchall()
    cur.close()
    conn.close()
    return recipes


def toggle_favorite_db(user_id, recipe_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM favorite
        WHERE user_id = %s AND recipe_id = %s
    """, (user_id, recipe_id))

    existing = cur.fetchone()

    if existing:
        cur.execute("""
            DELETE FROM favorite
            WHERE user_id = %s AND recipe_id = %s
        """, (user_id, recipe_id))
        status = "removed"
    else:
        cur.execute("""
            INSERT INTO favorite (user_id, recipe_id)
            VALUES (%s, %s)
        """, (user_id, recipe_id))
        status = "added"

    conn.commit()
    cur.close()
    conn.close()

    return status
