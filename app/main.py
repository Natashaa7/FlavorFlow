from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware

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
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
    email = data["email"]
    username = data["username"]
    phone = data["phonenumber"]
    password = data["password"]

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (email, username, phonenumber, password) VALUES (%s, %s, %s, %s)",
            (email, username, phone, password)
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
