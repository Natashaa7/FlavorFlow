from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import auth_controller, adminDb_controller, adminProfile_controller, cookbook_controller, generateRecipe_controller, index_controller, ingredManage_controller, userManage_controller, shareRecipe_controller, page_controller, profile_controller, forgotpw_controller,  resetpw_controller, viewRecipe_controller
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="flavorflowsecret")


# Mount static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Upload files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth_controller.router)
app.include_router(adminDb_controller.router)
app.include_router(adminProfile_controller.router)
app.include_router(cookbook_controller.router)
app.include_router(generateRecipe_controller.router)
app.include_router(index_controller.router)
app.include_router(ingredManage_controller.router)
app.include_router(page_controller.router)
app.include_router(profile_controller.router)
app.include_router(shareRecipe_controller.router)
app.include_router(userManage_controller.router)
app.include_router(forgotpw_controller.router)
app.include_router(resetpw_controller.router)
app.include_router(viewRecipe_controller.router)
# Login page (first page)








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

    redirect_url = "/admin-dashboard" if user["username"].lower() == "admin" else "/index"
    return RedirectResponse(url=redirect_url, status_code=303)

"""


