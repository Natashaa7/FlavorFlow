from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("pages/admin-dashboard.html", {"request": request})
