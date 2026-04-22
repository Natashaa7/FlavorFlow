from app.db.session import get_db_connection
from psycopg2.extras import RealDictCursor

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

    try:
        cur.execute("SELECT id FROM recipe WHERE id=%s", (recipe_id,))
        if not cur.fetchone():
            return {
                "success": False,
                "message": "Recipe not found"
            }

        cur.execute("""
            SELECT id FROM favorite
            WHERE user_id=%s AND recipe_id=%s
        """, (user_id, recipe_id))

        existing = cur.fetchone()

        if existing:
            cur.execute("""
                DELETE FROM favorite
                WHERE user_id=%s AND recipe_id=%s
            """, (user_id, recipe_id))
            action = "removed"
        else:
            cur.execute("""
                INSERT INTO favorite (user_id, recipe_id)
                VALUES (%s, %s)
            """, (user_id, recipe_id))
            action = "added"

        conn.commit()

        return {
            "success": True,
            "action": action
        }

    finally:
        cur.close()
        conn.close()

        
def get_recipe_by_id(recipe_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT id, title, description, image_path, cook_time, difficulty
            FROM recipe
            WHERE id=%s
        """, (recipe_id,))

        return cur.fetchone()

    finally:
        cur.close()
        conn.close()

def get_top_favorite_recipes(limit=6):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT 
            r.id,
            r.title,
            r.description,
            r.cook_time,
            r.difficulty,
            r.image_path,
            r.views,
            u.username,
            COUNT(f.id) AS favorite_count
        FROM recipe r
        JOIN users u ON r.user_id = u.id
        LEFT JOIN favorite f ON r.id = f.recipe_id
        GROUP BY r.id, u.username
        ORDER BY favorite_count DESC, r.views DESC
        LIMIT %s
    """, (limit,))

    recipes = cur.fetchall()
    cur.close()
    conn.close()
    return recipes
