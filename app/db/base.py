from app.db.session import get_db_connection


def execute_query(query: str, params: tuple = None, fetch: bool = False):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(query, params or ())

        if fetch:
            result = cur.fetchall()
        else:
            result = None

        conn.commit()
        return result

    finally:
        cur.close()
        conn.close()
