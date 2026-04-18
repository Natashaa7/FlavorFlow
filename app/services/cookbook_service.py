from app.db.session import get_db_connection

def get_user_recipes(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT r.*
        FROM recipe r
        JOIN favorite f ON r.id = f.recipe_id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC
    """, (user_id,))

    recipes = cur.fetchall()

    cur.close()
    conn.close()

    return recipes
