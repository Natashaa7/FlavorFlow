from fastapi import APIRouter, Request, HTTPException
from app.core.security import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/dashboard")
async def admin_dashboard_api(request: Request):
    user = get_current_user(request)

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    return {
        "success": True,
        "message": "Admin dashboard access granted",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    }
