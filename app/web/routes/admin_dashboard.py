from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.security import require_admin
from app.services.dashboard_service import (
    get_full_dashboard_data
)

router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(require_admin)]
)

templates = Jinja2Templates(directory="app/templates")


# -------------------------
# ADMIN DASHBOARD PAGE
# -------------------------
@router.get("/admin_dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):

    data = get_full_dashboard_data()

    return templates.TemplateResponse(
        "pages/admin_dashboard.html",
        {
            "request": request,

            # STATS (NOW USED IN JINJA)
            "stats": data.get("stats", {}),

            # CHART DATA
            "ingredient_categories": data.get("ingredient_categories", []),

            # TABLE DATA
            "top_ingredients": data.get("top_ingredients", []),
            "active_user": data.get("active_user", {})
        }
    )




