from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.core.security import require_user
from app.services.recipe_service import get_recipe_by_id

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/view-recipe/{recipe_id}", response_class=HTMLResponse)
def view_recipe(
    request: Request,
    recipe_id: int,
    user=Depends(require_user)   # USER ONLY ACCESS
):

    recipe = get_recipe_by_id(recipe_id)

    if not recipe:
        return HTMLResponse("Recipe not found", status_code=404)

    return templates.TemplateResponse(
        "pages/view_recipe.html",
        {
            "request": request,
            "recipe": recipe,
            "user": user
        }
    )
