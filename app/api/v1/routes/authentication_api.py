from fastapi import APIRouter, HTTPException
from app.schemas.user import SignupForm
from app.services.authentication_service import create_user, authenticate_user

router = APIRouter()


@router.get("/users")
async def get_users():
    from app.services.authentication_service import get_all_users
    return {"success": True, "data": get_all_users()}


@router.post("/signup")
async def signup_api(form: SignupForm):
    result = create_user(form.dict())

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return {"success": True, "user_id": result["user_id"]}


@router.post("/login")
async def login_api(username: str, password: str):
    user = authenticate_user(username, password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "success": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "is_admin": user["is_admin"],
        }
    }
