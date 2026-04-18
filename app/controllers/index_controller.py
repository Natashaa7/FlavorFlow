from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
from app.utils.session_utils import read_session

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

# Home page after login
@router.get("/index", response_class=HTMLResponse)
def home(request: Request):
    # Get user_id from session (if logged in)
    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token) if session_token else None

    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch recipes, username, and whether they are favorited by this user
    cur.execute("""
        SELECT r.id, r.title, r.description, r.cook_time, r.difficulty, r.image_path, r.views, u.username,
               CASE WHEN f.id IS NOT NULL THEN TRUE ELSE FALSE END AS is_favorited
        FROM recipe r
        JOIN users u ON r.user_id = u.id
        LEFT JOIN favorite f
        ON r.id = f.recipe_id AND f.user_id = %s
        ORDER BY r.created_at DESC
    """, (user_id,))

    recipes = cur.fetchall()  # Use RealDictCursor if you want dicts

    cur.close()
    conn.close()

    return templates.TemplateResponse(
        "index.html", {"request": request, "recipes": recipes}
    )   

@router.post("/toggle-favorite/{recipe_id}")
def toggle_favorite(recipe_id: int, request: Request):
    session_token = request.cookies.get("session_id")
    if not session_token:
        return RedirectResponse(url="/", status_code=303)

    user_id = read_session(session_token)
    if not user_id:
        return RedirectResponse(url="/", status_code=303)
    print("USER ID:", user_id)

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if already favorited
    cur.execute("""
        SELECT id FROM favorite
        WHERE user_id = %s AND recipe_id = %s
    """, (user_id, recipe_id))

    existing = cur.fetchone()

    if existing:
        # Remove favorite
        cur.execute("""
            DELETE FROM favorite
            WHERE user_id = %s AND recipe_id = %s
        """, (user_id, recipe_id))
        status = "removed"
    else:
        # Add favorite
        cur.execute("""
            INSERT INTO favorite (user_id, recipe_id)
            VALUES (%s, %s)
        """, (user_id, recipe_id))
        status = "added"
        print("USER ID:", user_id)


    conn.commit()
    cur.close()
    conn.close()

    return JSONResponse({"status": status})