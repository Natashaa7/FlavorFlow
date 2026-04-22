from itsdangerous import URLSafeSerializer, BadSignature
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from app.core.config import settings
from app.services.user_service import get_user_by_id

serializer = URLSafeSerializer(settings.SECRET_KEY, salt="session")


# -------------------------
# CREATE SESSION
# -------------------------
def create_session(user_id: int, expires_in_hours: int = 24):
    payload = {
        "user_id": user_id,
        "exp": (datetime.utcnow() + timedelta(hours=expires_in_hours)).timestamp()
    }
    return serializer.dumps(payload)


# -------------------------
# READ SESSION
# -------------------------
def read_session(token: str):
    try:
        data = serializer.loads(token)

        if "exp" not in data or "user_id" not in data:
            return None

        if datetime.utcnow().timestamp() > data["exp"]:
            return None

        return data["user_id"]

    except BadSignature:
        return None


# -------------------------
# CURRENT USER
# -------------------------
def get_current_user(request: Request):
    token = request.cookies.get("session_id")
    print(f"Token from cookie: {token}")  # Debugging line
    if not token:
        return None

    user_id = read_session(token)

    if not user_id:
        return None

    return get_user_by_id(user_id)


# -------------------------
# REQUIRE LOGIN
# -------------------------
def require_user(request: Request):
    user = get_current_user(request)

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return user


# -------------------------
# REQUIRE ADMIN ONLY
# -------------------------
def require_admin(request: Request):
    user = require_user(request)

    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")

    return user
