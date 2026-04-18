from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.pipeline import process_request
from app.core.security import require_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# -------------------------
# PAGE LOAD (LOGIN REQUIRED)
# -------------------------
@router.get("/generate_recipe", response_class=HTMLResponse)
async def generate_recipe_page(
    request: Request,
    user=Depends(require_user)
):
    return templates.TemplateResponse(
        "pages/generate_recipe.html",
        {
            "request": request,
            "user": user
        }
    )
