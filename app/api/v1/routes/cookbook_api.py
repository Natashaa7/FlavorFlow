from fastapi import APIRouter, Request, HTTPException
from app.core.security import read_session
from app.services.cookbook_service import get_user_recipes

router = APIRouter()


@router.get("/cookbook")
def cookbook_api(request: Request):

    session_token = request.cookies.get("session_id")
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = read_session(session_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    recipes = get_user_recipes(user_id)

    return {
        "success": True,
        "user_id": user_id,
        "recipes": recipes
    }
