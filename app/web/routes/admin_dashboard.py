from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.security import require_admin, require_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin_dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    user=Depends(require_admin)  
):

    return templates.TemplateResponse(
        "pages/admin_dashboard.html",
        {"request": request, "user": user}
    )
