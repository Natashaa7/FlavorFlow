from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.web.routes import (
    admin_dashboard, authentication, contactus, cookbook, forgot_password, generate_recipe, google_oauth, index, ingredient, logout, messages, pages, profile, reset_password, share_recipe, user_manage, view_recipe
)
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="flavorflowsecret")

# Mount static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Upload files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include api routers
app.include_router(api_router, prefix="/api/v1")

# include web routers
app.include_router(admin_dashboard.router)
app.include_router(authentication.router)
app.include_router(contactus.router)
app.include_router(cookbook.router) 
app.include_router(forgot_password.router)
app.include_router(generate_recipe.router)
app.include_router(google_oauth.router)
app.include_router(index.router)
app.include_router(ingredient.router)
app.include_router(logout.router)
app.include_router(messages.router)
app.include_router(pages.router)
app.include_router(profile.router)
app.include_router(reset_password.router)
app.include_router(share_recipe.router)
app.include_router(user_manage.router)
app.include_router(view_recipe.router)


"""
# --- SIGNUP ---
@app.post("/signup")
async def signup(
    email: str = Form(...),
    username: str = Form(...),
    phonenumber: str = Form(...),
    password: str = Form(...)
):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, username, phonenumber, password) VALUES (%s, %s, %s, %s)",
        (email, username, phonenumber, hashed_password)
    )
    conn.commit()
    cur.close()
    conn.close()

    return RedirectResponse(url="/?success=signup", status_code=303)

@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT username, password FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return RedirectResponse(url="/?error=login", status_code=303)

    if not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        return RedirectResponse(url="/?error=login", status_code=303)

    redirect_url = "/admin/admin_dashboard" if user["username"].lower() == "admin" else "/index"
    return RedirectResponse(url=redirect_url, status_code=303)

"""


