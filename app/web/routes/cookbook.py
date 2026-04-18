from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.security import require_user
from app.services.cookbook_service import get_user_recipes

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/cookbook", response_class=HTMLResponse)
def cookbook_page(request: Request, user=Depends(require_user)):

    # user is guaranteed to exist here
    recipes = get_user_recipes(user["id"])

    return templates.TemplateResponse(
        "pages/cookbook.html",
        {
            "request": request,
            "recipes": recipes,
            "user": user
        }
    )
