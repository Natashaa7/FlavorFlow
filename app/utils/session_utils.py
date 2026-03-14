from itsdangerous import URLSafeSerializer
from fastapi import Request
from app.database.connection import get_db_connection
from psycopg2.extras import RealDictCursor

SECRET_KEY = "your-super-secret-key"
serializer = URLSafeSerializer(SECRET_KEY, salt="session")

def create_session(user_id: int):
    return serializer.dumps({"user_id": user_id})

def read_session(session_cookie: str):
    try:
        data = serializer.loads(session_cookie)
        return data["user_id"]
    except:
        return None

def get_current_user(request: Request):
    session_cookie = request.cookies.get("session_id")
    if not session_cookie:
        return None

    user_id = read_session(session_cookie)  # decode the signed session cookie
    if not user_id:
        return None

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user
