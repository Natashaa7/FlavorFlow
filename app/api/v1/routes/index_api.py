from fastapi import APIRouter, Request, HTTPException
from app.core.security import read_session
from app.services.index_service import get_all_recipes, toggle_favorite_db

router = APIRouter()


@router.get("/recipes")
async def get_recipes_api(request: Request):

    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token) if session_token else None

    recipes = get_all_recipes(user_id)

    return {
        "success": True,
        "data": recipes
    }


from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.security import read_session

from app.core.security import require_user
from app.services.index_service import get_all_recipes, toggle_favorite_db, get_recipe_by_id

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

@router.post("/favorite/{recipe_id}")
async def toggle_favorite_api(recipe_id: int, request: Request):

    session_token = request.cookies.get("session_id")

    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = read_session(session_token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = toggle_favorite_db(user_id, recipe_id)

    if not result["success"]:
        raise HTTPException(
            status_code=404,
            detail=result["message"]
        )

    recipe = get_recipe_by_id(recipe_id)

    return {
        "success": True,
        "action": result["action"],
        "recipe": recipe
    }

