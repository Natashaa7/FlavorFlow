from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
import os, shutil, uuid
from passlib.context import CryptContext
import bcrypt

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Templates folder
templates = Jinja2Templates(directory="app/templates")

# Login page (first page)
@app.get("/", response_class=HTMLResponse)
async def authenticate(request: Request):
    return templates.TemplateResponse("pages/authenticate.html", {"request": request})

# Home page after login
@app.get("/index", response_class=HTMLResponse)
def home(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT title, description, cook_time, difficulty, image_path
        FROM recipe
        ORDER BY created_at DESC
    """)

    recipes = cur.fetchall()  # list of dicts because of RealDictCursor

    cur.close()
    conn.close()

    return templates.TemplateResponse(
        "index.html", {"request": request, "recipes": recipes}
    )

@app.get("/aboutus", response_class=HTMLResponse)
async def aboutus(request: Request):
    return templates.TemplateResponse("pages/aboutus.html", {"request": request})

@app.get("/contactus", response_class=HTMLResponse)
async def contactus(request: Request):
    return templates.TemplateResponse("pages/contactus.html", {"request": request})

@app.get("/cookbook", response_class=HTMLResponse)
async def cookbook(request: Request):
    return templates.TemplateResponse("pages/cookbook.html", {"request": request})

@app.get("/generate-recipe", response_class=HTMLResponse)
async def generate_recipe(request: Request):
    return templates.TemplateResponse("pages/generate-recipe.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("pages/profile.html", {"request": request})

@app.get("/share-recipe", response_class=HTMLResponse)
async def share_recipe(request: Request):
    return templates.TemplateResponse("pages/share-recipe.html", {"request": request})

@app.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("pages/admin-dashboard.html", {"request": request})

@app.get("/ad-base", response_class=HTMLResponse)
async def ad_base(request: Request):
    return templates.TemplateResponse("pages/ad-base.html", {"request": request})

"""@app.get("/user-manage", response_class=HTMLResponse)
async def ingredient_manage(request: Request):
    return templates.TemplateResponse("pages/user-manage.html", {"request": request})"""
    
@app.get("/user-manage", response_class=HTMLResponse)
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



@app.get("/ingredient-manage", response_class=HTMLResponse)
async def ingredient_manage(request: Request):
    return templates.TemplateResponse("pages/ingredient-manage.html", {"request": request})

@app.get("/ad-profile", response_class=HTMLResponse)
async def ad_base(request: Request):
    return templates.TemplateResponse("pages/ad-profile.html", {"request": request})

# Allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,  # important if sending cookies/auth headers
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = psycopg2.connect(
        dbname="flavorflow",
        user="natashababu",
        password=None,
        host="localhost",
        port="5432",
        cursor_factory=RealDictCursor   #return query as python dictionaries
    )
    print("Database connected")   # prints when connection is successful
    return conn

@app.get("/users")
def read_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, email, username, phonenumber, password FROM users;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

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



# --- ensure folders exist ---
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/files", exist_ok=True)

# Upload files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.post("/add-recipe")
async def add_recipe(
    title: str = Form(...),
    description: str = Form(...),
    cook_time: int = Form(...),
    difficulty: str = Form(...),
    image: UploadFile = File(...),
    file: UploadFile = File(...)
):
    # --- basic validation ---
    if difficulty not in ["Easy", "Intermediate", "Hard"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty")

    # --- create unique filenames ---
    image_name = f"{uuid.uuid4()}_{os.path.basename(image.filename)}"
    file_name = f"{uuid.uuid4()}_{os.path.basename(file.filename)}"

    image_path = f"uploads/images/{image_name}"
    file_path = f"uploads/files/{file_name}"

    # --- save image ---
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    image.file.close()

    # --- save file ---
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file.file.close()

    # --- insert into database ---
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO recipe
            (title, description, image_path, file_path, cook_time, difficulty)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                title,
                description,
                "/" + image_path,  # optional leading slash
                "/" + file_path,
                cook_time,
                difficulty
            )
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        print("DB Error:", e)
        raise HTTPException(status_code=500, detail="Failed to add recipe")

    finally:
        cur.close()
        conn.close()

    # --- redirect back to share page with success ---
    return RedirectResponse(url="/share-recipe?success=1", status_code=303)



# add users

@app.post("/add-users")
async def add_users(
    email: str = Form(...),
    username: str = Form(...),
    phonenumber: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    
    # ✅ Check passwords match
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
