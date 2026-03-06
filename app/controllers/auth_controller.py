from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import bcrypt
from app.database.connection import get_db_connection
from app.utils.session_utils import create_session
from pydantic import ValidationError
from datetime import datetime
from app.models.user_model import SignupForm
from authlib.integrations.starlette_client import OAuth

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
    return templates.TemplateResponse("pages/authenticate.html", {"request": request})

@router.post("/signup")
async def signup(
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phonenumber: str = Form(...),
    dob: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    # Validate input
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
        return RedirectResponse(url=f"/?error={e.errors()[0]['msg']}", status_code=303)

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email, username, phonenumber, dob, password) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (name, email, username, phonenumber, dob, hashed_password)
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    response = RedirectResponse(url="/index", status_code=303)
    # Create session cookie
    session_token = create_session(user_id)
    response.set_cookie(key="session_id", value=session_token, httponly=True)
    return response

@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        cur.close()
        conn.close()
        return RedirectResponse(url="/?error=login", status_code=303)

    # Update last login
    cur.execute("UPDATE users SET last_login=%s WHERE id=%s", (datetime.utcnow(), user["id"]))
    conn.commit()
    cur.close()
    conn.close()

    # Create session cookie
    response = RedirectResponse(url="/index", status_code=303)
    session_token = create_session(user["id"])
    response.set_cookie(key="session_id", value=session_token, httponly=True)
    return response

# --- OAuth setup (placeholders) ---
oauth = OAuth()
oauth.register(
    name='google',
    client_id='YOUR_GOOGLE_CLIENT_ID',
    client_secret='YOUR_GOOGLE_CLIENT_SECRET',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'}
)

# ======================
# --- OAuth PLACEHOLDERS ---
# ======================
@router.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)
    # TODO: check user in DB, create if not exists, update last_login
    # Then set session cookie like in login
    return RedirectResponse(url="/index", status_code=303)