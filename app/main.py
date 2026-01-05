from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
import os, shutil, uuid


app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

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

@app.post("/signup")
async def signup(request: Request):
    data = await request.json()

    email = data.get("email")
    username = data.get("username")
    phone = data.get("phonenumber")
    password = data.get("password")

    if not all([email, username, phone, password]):
        return {"error": "All fields are required"}

    hashed_password = pwd_context.hash(password)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO users (email, username, phonenumber, password)
            VALUES (%s, %s, %s, %s)
            """,
            (email, username, phone, hashed_password)
        )
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return {"error": "Email, username, or phone already exists"}
    finally:
        cur.close()
        conn.close()

    return {"message": "User registered successfully"}


@app.post("/login")
async def login(request: Request):
    data = await request.json()
    username = data["username"]
    password = data["password"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        return {"message": "Login successful", "user": user}
    else:
        return {"error": "Invalid username or password"}


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
    if difficulty not in ["Easy", "Medium", "Hard"]:
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
