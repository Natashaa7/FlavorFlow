from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
from app.utils.session_utils import read_session
from psycopg2.extras import RealDictCursor
import bcrypt

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    session_token = request.cookies.get("session_id")
    if not session_token:
        return RedirectResponse(url="/", status_code=303)

    user_id = read_session(session_token)
    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT name, email, username, phonenumber, dob, created_at FROM users WHERE id=%s",
        (user_id,)
    )
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        "pages/profile.html",
        {"request": request, "user": user}
    )

@router.post("/upd-profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phonenumber: str = Form(...),
    dob: str = Form(...),
    password: str = Form(None),
    confirm_password: str = Form(None)
):
    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)
    if not user_id:
        return RedirectResponse(url="/authenticate", status_code=303)

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Fetch current user info
    cur.execute(
        "SELECT name, email, username, phonenumber, dob, password, created_at FROM users WHERE id=%s",
        (user_id,)
    )
    user = cur.fetchone()
    if not user:
        cur.close()
        conn.close()
        return RedirectResponse(url="pages/profile.html", status_code=303)

    stored_password = user["password"]

    # Password update logic
    if password:
        if password != confirm_password:
            cur.close()
            conn.close()
            return templates.TemplateResponse(
                "pages/profile.html",
                {"request": request, "user": user, "error": "Passwords do not match!"}
            )
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    else:
        hashed_password = stored_password

    # Update user
    cur.execute(
        """
        UPDATE users
        SET name=%s, username=%s, email=%s, phonenumber=%s, dob=%s, password=%s
        WHERE id=%s
        """,
        (name, username, email, phonenumber, dob, hashed_password, user_id)
    )
    conn.commit()

    # Fetch updated user (exclude password for template)
    cur.execute(
        "SELECT name, email, username, phonenumber, dob, created_at FROM users WHERE id=%s",
        (user_id,)
    )
    updated_user = cur.fetchone()
    cur.close()
    conn.close()

    return templates.TemplateResponse(
        "pages/profile.html",
        {"request": request, "user": updated_user, "success": "Profile updated successfully!"}
    )
