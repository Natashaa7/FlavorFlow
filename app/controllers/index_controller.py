from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

# Home page after login
@router.get("/index", response_class=HTMLResponse)
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