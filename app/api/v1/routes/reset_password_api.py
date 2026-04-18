from fastapi import APIRouter, HTTPException
from app.services.reset_pw_service import verify_reset_code, reset_user_password
from app.core.security import create_session

router = APIRouter()


@router.post("/reset-password")
async def reset_password_api(email: str, code: str, new_password: str, confirm_password: str):

    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user, error = verify_reset_code(email, code)

    if error:
        raise HTTPException(status_code=400, detail=error)

    if not user or "id" not in user:
        raise HTTPException(status_code=400, detail="Invalid user or reset code")

    try:
        reset_user_password(email, new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    session_token = create_session(user["id"])

    return {
        "success": True,
        "message": "Password reset successful",
        "session": session_token
    }
