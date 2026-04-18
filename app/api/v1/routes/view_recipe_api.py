from fastapi import APIRouter, HTTPException
from app.services.recipe_service import get_recipe_by_id

router = APIRouter()


@router.get("/{recipe_id}")
async def get_recipe_api(recipe_id: int):

    recipe = get_recipe_by_id(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {
        "success": True,
        "data": recipe
    }
