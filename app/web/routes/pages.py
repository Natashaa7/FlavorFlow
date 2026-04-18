from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.security import require_user, require_admin

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# -------------------------
# PUBLIC PAGE
# -------------------------
@router.get("/", response_class=HTMLResponse)
async def welcome(request: Request):

    return templates.TemplateResponse(
        "pages/welcome.html",
        {"request": request}
    )


# -------------------------
# USER ONLY: ABOUT US
# -------------------------
@router.get("/aboutus", response_class=HTMLResponse)
async def aboutus(request: Request, user=Depends(require_user)):

    return templates.TemplateResponse(
        "pages/aboutus.html",
        {
            "request": request,
            "user": user
        }
    )


# -------------------------
# USER ONLY: CONTACT US
# -------------------------
@router.get("/contactus", response_class=HTMLResponse)
async def contactus(request: Request, user=Depends(require_user)):

    return templates.TemplateResponse(
        "pages/contactus.html",
        {
            "request": request,
            "user": user
        }
    )


# -------------------------
# ADMIN ONLY PAGE
# -------------------------
@router.get("/ad-base", response_class=HTMLResponse)
async def ad_base(request: Request, user=Depends(require_admin)):

    return templates.TemplateResponse(
        "pages/ad-base.html",
        {
            "request": request,
            "user": user
        }
    )
