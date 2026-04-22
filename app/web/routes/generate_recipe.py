import os, uuid, json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db.session import get_db_connection
from app.services.pipeline import process_request
from app.core.security import require_user

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/generate_recipe")
async def generate_recipe_page(request: Request, user=Depends(require_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, category
        FROM ingredients
    """)

    rows = cur.fetchall()

    grouped = {}

    for r in rows:
        name = r["name"] if isinstance(r, dict) else r[0]
        category = r["category"] if isinstance(r, dict) else r[1]

        grouped.setdefault(category, []).append(name)

    return templates.TemplateResponse(
        "pages/generate_recipe.html",
        {
            "request": request,
            "ingredients": grouped
        }
    )

# -----------------------------
# 5. HISTORY API
# -----------------------------
@router.get("/history")
async def get_history(user=Depends(require_user)):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, recipe_title, recipe_text, ingredients, images, nutritional_json, created_at
        FROM recipe_history
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (user["id"],))  

    rows = cur.fetchall()

    return [
        {
            "id": r[0],
            "title": r[1],
            "recipe": r[2],
            "ingredients": r[3],
            "images": r[4],
            "nutrition": r[5],
            "created_at": r[6].isoformat() if r[6] else None
        }
        for r in rows
    ]
