from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

@router.get("/aboutus", response_class=HTMLResponse)
async def aboutus(request: Request):
    return templates.TemplateResponse("pages/aboutus.html", {"request": request})

@router.get("/contactus", response_class=HTMLResponse)
async def contactus(request: Request):
    return templates.TemplateResponse("pages/contactus.html", {"request": request})

@router.get("/ad-base", response_class=HTMLResponse)
async def ad_base(request: Request):
    return templates.TemplateResponse("pages/ad-base.html", {"request": request})
