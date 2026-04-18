from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.services.recipe_service import get_recipe_by_id

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/view-recipe/{recipe_id}", response_class=HTMLResponse)
def view_recipe(request: Request, recipe_id: int):

    recipe = get_recipe_by_id(recipe_id)

    if not recipe:
        return HTMLResponse("Recipe not found", status_code=404)

    return templates.TemplateResponse(
        "pages/view_recipe.html",
        {
            "request": request,
            "recipe": recipe
        }
    )
