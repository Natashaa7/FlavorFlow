from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
from app.models.user_model import SignupForm

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

@router.get("/user-manage", response_class=HTMLResponse)
async def user_manage(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, email, username, phonenumber
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
        "INSERT INTO users (email, username, phonenumber, password) VALUES (%s, %s, %s, %s)",
        (email, username, phonenumber, hashed_password)
    )

    conn.commit()
    cur.close()
    conn.close()

    return RedirectResponse(url="/user-manage?success=added", status_code=303)
