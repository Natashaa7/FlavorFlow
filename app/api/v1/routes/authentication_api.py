from fastapi import APIRouter, HTTPException, status
from app.schemas.user import SignupForm
from app.services.authentication_service import create_user, authenticate_user
from fastapi import Form

router = APIRouter()

@router.get("/users")
async def get_users():
    from app.services.authentication_service import get_all_users
    return {"success": True, "data": get_all_users()}


@router.post("/signup")
async def signup_api(form: SignupForm):
    result = create_user(form.dict())

    if not result["success"]:
        # Handle duplicate cases → 409 Conflict
        if result["error"] in ["Email already registered", "Username already taken"]:
            raise HTTPException(
                status_code=409,
                detail=result["error"]
            )

        # Other failures → 400 Bad Request
        raise HTTPException(
            status_code=400,
            detail=result["error"]
        )

    return {
        "success": True,
        "message": "User created successfully",
        "data": {
            "user_id": result["user_id"]
        }
    }



@router.post("/login")
async def login_api(username: str = Form(...), password: str = Form(...)):

    user = authenticate_user(username, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login failed: Invalid credentials"
        )

    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "id": user["id"],
            "username": user["username"],
            "is_admin": user["is_admin"]
        }
    }
