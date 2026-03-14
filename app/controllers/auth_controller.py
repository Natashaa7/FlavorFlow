from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from psycopg2.extras import RealDictCursor
import bcrypt
from app.database.connection import get_db_connection
from app.utils.session_utils import create_session
from pydantic import ValidationError
from datetime import datetime
from app.models.user_model import SignupForm
import os
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth
import secrets


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/users")
def read_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, email, username, phonenumber, password FROM users;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

@router.get("/", response_class=HTMLResponse)
async def authenticate(request: Request):
    return templates.TemplateResponse(
        "pages/authenticate.html",
        {
            "request": request,
            "active_form": "login"   # default form
        }
    )

@router.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phonenumber: str = Form(...),
    dob: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    try:
        form = SignupForm(
            name=name,
            username=username,
            email=email,
            phonenumber=phonenumber,
            dob=dob,
            password=password,
            confirm_password=confirm_password
        )
    except ValidationError as e:
        # Collect all error messages as a list
        error_messages = [err['msg'] for err in e.errors()]
        return templates.TemplateResponse(
            "pages/authenticate.html",
            {
                "request": request,
                "errors": error_messages,  # list of error strings
                "form_data": {
                    "name": name,
                    "username": username,
                    "email": email,
                    "phonenumber": phonenumber,
                    "dob": dob
                },
                "active_form": "signup"  # must always be present
            }
        )
        
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        INSERT INTO users (name, email, username, phonenumber, dob, password, is_admin, oauth_provider)
        VALUES (%s, %s, %s, %s, %s, %s, FALSE, %s)
        RETURNING id
        """,
        (name, email, username, phonenumber, dob, hashed_password, 'local')
    )
    user_id = cur.fetchone()["id"]

    cur.execute("UPDATE users SET last_login=%s WHERE id=%s", (datetime.utcnow(), user["id"]))
    conn.commit()
    cur.close()
    conn.close()
    
    # Show success message on form page
    return templates.TemplateResponse(
        "pages/authenticate.html",
        {
            "request": request,
            "success": "Account created successfully!"
        }
    )
    
@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    errors = []

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        errors.append("Invalid username or password")
        return templates.TemplateResponse(
            "pages/authenticate.html",
            {
                "request": request,
                "errors": errors,
                "active_form": "login",
                "form_data": {"username": username}
            }
        )

    # Update last login
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("UPDATE users SET last_login=%s WHERE id=%s", (datetime.utcnow(), user["id"]))
    conn.commit()
    cur.close()
    conn.close()

    # Decide redirect based on role
    if user["is_admin"]:
        redirect_url = "/admin-dashboard"
    else:
        redirect_url = "/index"

    response = templates.TemplateResponse(
        "pages/authenticate.html", {"request": request}  # Temporary, cookie will redirect
    )
    session_token = create_session(user["id"])
    response.set_cookie(key="session_id", value=session_token, httponly=True)
    return RedirectResponse(url=redirect_url, status_code=303)

# --- OAuth setup (placeholders) ---

load_dotenv("/Users/natashababu/Documents/FYP/flavorflow/app/secret.env")

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

print(os.getenv("GOOGLE_CLIENT_ID"))
print(os.getenv("GOOGLE_CLIENT_SECRET"))


# --- OAuth PLACEHOLDERS ---
@router.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(
        request, 
        redirect_uri,
        prompt="select_account"   # forces account selection
    )

@router.get("/auth/google/callback")
async def google_callback(request: Request):

    token = await oauth.google.authorize_access_token(request)
    resp = await oauth.google.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        token=token
    )
    user_info = resp.json()

    email = user_info["email"]
    name = user_info["name"]
    username = email.split("@")[0]

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Check if user exists
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user:
        # Insert user without a password
        cur.execute("""
            INSERT INTO users (name, email, username, password, is_admin, oauth_provider)
            VALUES (%s, %s, %s, NULL, FALSE, %s)
            RETURNING id
        """, (name, email, username, 'google'))
        user_id = cur.fetchone()["id"]
        conn.commit()
    else:
        user_id = user["id"]

    cur.execute(
        "UPDATE users SET last_login=%s WHERE id=%s",
        (datetime.utcnow(), user_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    # Create session
    session_token = create_session(user_id)

    # Redirect based on admin status
    redirect_url = "/admin-dashboard" if user and user.get("is_admin") else "/index"
    response = RedirectResponse(redirect_url, status_code=303)
    response.set_cookie(key="session_id", value=session_token, httponly=True)
    return response


