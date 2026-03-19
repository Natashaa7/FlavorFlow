from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
from app.utils.session_utils import read_session

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

@router.get("/cookbook", response_class=HTMLResponse)
def favorites(request: Request):

    session_token = request.cookies.get("session_id")
    if not session_token:
        return RedirectResponse(url="/", status_code=303)

    user_id = read_session(session_token)
    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT r.*
        FROM recipe r
        JOIN favorite f ON r.id = f.recipe_id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC
    """, (user_id,))

    recipes = cur.fetchall()
    print("Cookbook USER:", user_id)
    print("Recipes:", recipes)

    cur.close()
    conn.close()

    return templates.TemplateResponse(
        "pages/cookbook.html",
        {"request": request, "recipes": recipes}
    )
