from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

app = FastAPI()

# Allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"], 
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
        cursor_factory=RealDictCursor  #return query as python dictionaries
    )
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
