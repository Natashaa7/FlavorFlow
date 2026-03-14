from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
import bcrypt
from psycopg2.extras import RealDictCursor
from datetime import datetime
from app.utils.session_utils import create_session

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# -----------------------------
# GET: Show Reset Password Page
# -----------------------------
@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("pages/reset_password.html", {"request": request})

# -----------------------------
# POST: Handle Reset Password
# -----------------------------
@router.post("/reset-password", response_class=HTMLResponse)
async def reset_password(
    request: Request,
    email: str = Form(...),
    code: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    # Validate passwords
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "pages/reset_password.html",
            {"request": request, "error": "New password and confirm password do not match."}
        )

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Get user
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return templates.TemplateResponse(
            "pages/reset_password.html",
            {"request": request, "error": "Invalid request. Email not registered."}
        )

    # Validate code and expiry
    if user["reset_code"] != code or datetime.utcnow() > user["reset_code_expiry"]:
        cur.close()
        conn.close()
        return templates.TemplateResponse(
            "pages/reset_password.html",
            {"request": request, "error": "Invalid or expired reset code."}
        )

    # Hash new password
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

    # Update password and reset code fields for this user
    # After updating password
    cur.execute("""
        UPDATE users
        SET password=%s,
            reset_code=NULL,
            reset_code_expiry=NULL
        WHERE email=%s
    """, (hashed, email))
    conn.commit()

    # Create a session for the user who reset the password
    session_token = create_session(user["id"])

    cur.close()
    conn.close()

    # Redirect to home page with session cookie
    response = RedirectResponse(url="/index", status_code=303)
    response.set_cookie(key="session_id", value=session_token, httponly=True)
    return response