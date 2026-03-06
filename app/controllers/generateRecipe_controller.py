from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

@router.get("/generate-recipe", response_class=HTMLResponse)
async def generate_recipe(request: Request):
    return templates.TemplateResponse("pages/generate-recipe.html", {"request": request})

