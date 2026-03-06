from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

@router.get("/ingredient-manage", response_class=HTMLResponse)
async def ingredient_manage(request: Request):
    return templates.TemplateResponse("pages/ingredient-manage.html", {"request": request})
