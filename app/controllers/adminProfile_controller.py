from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
from app.utils.session_utils import read_session
from psycopg2.extras import RealDictCursor
import bcrypt

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/ad-profile", response_class=HTMLResponse)
async def profile(request: Request):

    session_token = request.cookies.get("session_id")
    if not session_token:
        return RedirectResponse(url="/", status_code=303)

    user_id = read_session(session_token)
    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "SELECT name, email, username, phonenumber, dob, password, created_at FROM users WHERE id=%s",
        (user_id,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return templates.TemplateResponse(
        "pages/ad-profile.html",
        {"request": request, "user": user}
    )


@router.post("/update-profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phonenumber: str = Form(...),
    dob: str = Form(...),
    current_password: str = Form(None),
    password: str = Form(None),
    confirm_password: str = Form(None)
):

    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # get existing user
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()

    stored_password = user["password"]

    # -------------------------
    # Password Change Handling
    # -------------------------

    if password:  # user wants to change password

        # check current password entered
        if not current_password:
            return templates.TemplateResponse(
                "pages/ad-profile.html",
                {"request": request, "user": user, "error": "Please enter current password"}
            )

        if not bcrypt.checkpw(current_password.encode(), stored_password.encode()):
            return templates.TemplateResponse(
                "pages/ad-profile.html",
                {"request": request, "user": user, "error": "Current password is incorrect"}
            )

        if password != confirm_password:
            return templates.TemplateResponse(
                "pages/ad-profile.html",
                {"request": request, "user": user, "error": "Passwords do not match"}
            )

        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode()

    else:
        # keep old password
        hashed_password = stored_password

    # -------------------------
    # Update Profile
    # -------------------------

    cur.execute(
        """
        UPDATE users
        SET name=%s, username=%s, email=%s, phonenumber=%s, dob=%s, password=%s
        WHERE id=%s
        """,
        (name, username, email, phonenumber, dob, hashed_password, user_id)
    )

    conn.commit()

    # fetch updated user
    cur.execute(
        "SELECT name, email, username, phonenumber, dob, password, created_at FROM users WHERE id=%s",
        (user_id,)
    )
    user = cur.fetchone()

    return templates.TemplateResponse(
        "pages/ad-profile.html",
        {
            "request": request,
            "user": user,
            "error": "Current password is incorrect"
        }
    )

