from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.security import require_user
from app.services.index_service import get_all_recipes, toggle_favorite_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# -------------------------
# INDEX PAGE (USER ONLY)
# -------------------------
@router.get("/index", response_class=HTMLResponse)
def home(request: Request, user=Depends(require_user)):

    recipes = get_all_recipes(user["id"])

    return templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request,
            "recipes": recipes,
            "user": user
        }
    )

@router.post("/toggle-favorite/{recipe_id}")
def toggle_favorite(
    recipe_id: int,
    user=Depends(require_user)
):

    toggle_favorite_db(user["id"], recipe_id)

    return RedirectResponse(url="/index", status_code=303)
