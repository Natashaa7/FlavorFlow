from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.database.connection import get_db_connection
from psycopg2.extras import RealDictCursor

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_recipe_by_id(recipe_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)  # <- important
    cur.execute("""
        SELECT id, title, description, file_path
        FROM recipe
        WHERE id = %s
    """, (recipe_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    return row  # already a dict

@router.get("/view-recipe/{recipe_id}", response_class=HTMLResponse)
def view_recipe(request: Request, recipe_id: int):
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        return HTMLResponse("Recipe not found", status_code=404)
    return templates.TemplateResponse(
        "pages/view_recipe.html",
        {"request": request, "recipe": recipe}
    )
