from app.db.session import get_db_connection
from psycopg2.extras import RealDictCursor


def get_full_dashboard_data():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # ================= STATS =================
    cur.execute("""
        SELECT
            (SELECT COUNT(*) FROM users) AS users,
            (SELECT COUNT(*) FROM recipe) AS recipes,
            (SELECT COUNT(*) FROM ingredients) AS ingredients,
            (SELECT COUNT(*) FROM recipe WHERE created_at >= NOW() - INTERVAL '7 days') AS recipes_this_week
    """)
    stats = cur.fetchone()

    # ================= INGREDIENT CATEGORY DISTRIBUTION =================
    cur.execute("""
        SELECT 
            COALESCE(NULLIF(TRIM(category), ''), 'Uncategorized') AS category,
            COUNT(*)::int AS total
        FROM ingredients
        GROUP BY COALESCE(NULLIF(TRIM(category), ''), 'Uncategorized')
        ORDER BY total DESC
        """)
    ingredient_categories = [
    {
        "category": str(row["category"]),
        "total": int(row["total"])
    }
    for row in cur.fetchall()
]



    # ================= TOP INGREDIENTS =================
    cur.execute("""
        SELECT name, usage_count
        FROM ingredients
        ORDER BY usage_count DESC
        LIMIT 5
    """)
    top_ingredients = cur.fetchall()

    # ================= TOP USER (FIXED) =================
    cur.execute("""
        SELECT u.name, COUNT(r.id) AS total
        FROM recipe r
        JOIN users u ON u.id = r.user_id
        GROUP BY u.name
        ORDER BY total DESC
        LIMIT 1
    """)
    active_user = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "stats": stats,
        "ingredient_categories": ingredient_categories,
        "top_ingredients": top_ingredients,
        "active_user": active_user
    }
