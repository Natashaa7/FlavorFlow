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


@router.post("/favorite/{recipe_id}")
async def toggle_favorite_api(recipe_id: int, request: Request):

    session_token = request.cookies.get("session_id")

    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = read_session(session_token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    status = toggle_favorite_db(user_id, recipe_id)

    return {
        "success": True,
        "status": status
    }
