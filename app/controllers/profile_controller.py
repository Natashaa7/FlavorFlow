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
    # Get session token from cookie
    session_token = request.cookies.get("session_id")
    if not session_token:
        return RedirectResponse(url="/", status_code=303)

    # Decode session token to get user_id
    user_id = read_session(session_token)
    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    # Fetch user info from DB
    conn = get_db_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT name, email, username, phonenumber, dob, password, created_at FROM users WHERE id=%s",
        (user_id,)
    )
    user = cursor.fetchone()

    user_data = {
        "name": user["name"],
        "email": user["email"],
        "username": user["username"],
        "phonenumber": user["phonenumber"],
        "dob": user["dob"],
        "password": user["password"],
        "created_at": user["created_at"]
    }

    return templates.TemplateResponse(
        "pages/profile.html",
        {"request": request, "user": user_data}
    )

@router.post("/update-profile", response_class=HTMLResponse)
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
    # Get user_id from session cookie
    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)
    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Check if passwords match
    if password and password != confirm_password:
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return templates.TemplateResponse(
            "pages/profile.html",
            {"request": request, "user": user, "error": "Passwords do not match!"}
        )

    # Hash new password if provided, otherwise keep old password
    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()
    else:
        cur.execute("SELECT password FROM users WHERE id=%s", (user_id,))
        hashed_password = cur.fetchone()["password"]

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

    # Fetch updated user
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    updated_user = cur.fetchone()
    cur.close()
    conn.close()

    return templates.TemplateResponse(
        "pages/profile.html",
        {"request": request, "user": updated_user, "success": "Profile updated successfully!"}
    )
