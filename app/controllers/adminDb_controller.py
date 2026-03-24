from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.session_utils import get_current_user

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user = get_current_user(request)

    if not user:
        return RedirectResponse(url="/authenticate")  # Not logged in → redirect to login

    if not user["is_admin"]:
        return RedirectResponse(url="/index")  # Logged in but not admin → redirect home

    return templates.TemplateResponse(
        "pages/admin-dashboard.html",
        {"request": request, "user": user}
    )