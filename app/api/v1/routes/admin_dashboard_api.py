from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from app.core.security import get_current_user
from app.services.dashboard_service import get_full_dashboard_data

router = APIRouter()

# -------------------------
# ADMIN DASHBOARD API
# -------------------------
@router.get("/dashboard")
async def admin_dashboard_api(request: Request):

    # -------------------------
    # AUTH CHECK
    # -------------------------
    user = get_current_user(request)

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized")

    # -------------------------
    # DASHBOARD DATA (ONE CALL ONLY)
    # -------------------------
    data = get_full_dashboard_data()

    # -------------------------
    # RESPONSE
    # -------------------------
    return JSONResponse({
        "success": True,
        "message": "Admin dashboard access granted",

        "user": {
            "id": user.get("id"),
            "username": user.get("username"),
            "email": user.get("email")
        },

        "stats": data["stats"],
        "monthly": data["monthly"],
        "top_ingredients": data["top_ingredients"],
        "active_user": data["active_user"]
    })
