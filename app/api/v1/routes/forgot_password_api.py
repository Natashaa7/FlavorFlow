from fastapi import APIRouter, HTTPException
from app.services.forgot_pw_service import create_reset_code
from app.services.email_service import send_reset_email

router = APIRouter()


@router.post("/forgot-password")
async def forgot_password_api(email: str):

    if not email.strip():
        raise HTTPException(status_code=400, detail="Email field is required.")

    code = create_reset_code(email)

    if not code:
        raise HTTPException(status_code=404, detail="Email not registered.")

    send_reset_email(email, code)

    return {
    "success": True,
    "message": "Reset code sent to email.",
    "email": email,
    "reset_code": code
}

