from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.security import read_session

from app.core.security import require_user
from app.services.index_service import get_all_recipes, toggle_favorite_db, get_recipe_by_id, get_top_favorite_recipes

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# -------------------------
# INDEX PAGE (USER ONLY)
# -------------------------
@router.get("/index", response_class=HTMLResponse)
def home(request: Request, user=Depends(require_user)):

    top_recipes = get_top_favorite_recipes(limit=3)
    all_recipes = get_all_recipes(user["id"])

    login_success = request.cookies.get("login_success")

    response = templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request,
            "top_recipes": top_recipes,
            "all_recipes": all_recipes,
            "user": user,
            "login_success": login_success
        }
    )

    response.delete_cookie("login_success")

    return response



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
        raise HTTPException(status_code=404, detail=result["message"])

    recipe = get_recipe_by_id(recipe_id)

    return {
        "success": True,
        "action": result["action"],
        "recipe": recipe
    }
