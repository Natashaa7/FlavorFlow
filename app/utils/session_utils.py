from itsdangerous import URLSafeSerializer
from fastapi import Request

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
    if session_cookie:
        return read_session(session_cookie)
    return None
