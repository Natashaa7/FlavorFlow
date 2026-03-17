from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
from app.models.user_model import SignupForm
import bcrypt
from app.utils.session_utils import read_session
from typing import Optional

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

@router.get("/user-manage", response_class=HTMLResponse)
async def user_manage(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, email, username, phonenumber, password, name, dob, last_login, created_at, is_admin
    FROM users
    ORDER BY id DESC
    """)

    users = cur.fetchall()

    cur.close()
    conn.close()

    print(users)  # 👈 add this temporarily to debug

    return templates.TemplateResponse(
        "pages/user-manage.html",
        {"request": request, "users": users}
    )

# add users
@router.post("/add-users")
async def add_users(
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phonenumber: str = Form(...),
    dob: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    
    # Check passwords match
    if password != confirm_password:
        return RedirectResponse(
            url="/?error=password-mismatch",
            status_code=303
        )

    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode()

    conn = get_db_connection()
    cur = conn.cursor()

    # Optional but recommended: check if email exists
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cur.fetchone()

    if existing_user:
        cur.close()
        conn.close()
        return RedirectResponse(
            url="/?error=email-exists",
            status_code=303
        )

    cur.execute(
        "INSERT INTO users (email, username, phonenumber, dob, name, password) VALUES (%s, %s, %s, %s, %s, %s)",
        (email, username, phonenumber, dob, name, hashed_password)
    )

    conn.commit()
    cur.close()
    conn.close()

    return RedirectResponse(url="/user-manage?success=added", status_code=303)

@router.post("/update-users")
async def update_users(
    request: Request,
    id: int = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    phonenumber: str = Form(...),
    name: str = Form(...),
    dob: str = Form(...),
    password: Optional[str] = Form(None)
):

    session_token = request.cookies.get("session_id")
    admin_id = read_session(session_token)

    if not admin_id:
        return RedirectResponse(url="/", status_code=303)

    conn = get_db_connection()
    cur = conn.cursor()

    # 🔹 Base fields
    fields = [
        "email=%s",
        "username=%s",
        "phonenumber=%s",
        "name=%s",
        "dob=%s"
    ]

    values = [email, username, phonenumber, name, dob]

    # =========================
    # PASSWORD — only if given
    # =========================
    if password:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        fields.append("password=%s")
        values.append(hashed_pw)

    # WHERE clause
    values.append(id)

    cur.execute(
        f"""
        UPDATE users
        SET {', '.join(fields)}
        WHERE id=%s
        """,
        values
    )

    conn.commit()
    cur.close()
    conn.close()

    return RedirectResponse(url="/user-manage", status_code=303)

@router.post("/delete-users")
async def delete_users(
    request: Request,
    id: int = Form(...)
):
    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM users WHERE id=%s",
        (id, user_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return RedirectResponse(url="/manage-user", status_code=303)
