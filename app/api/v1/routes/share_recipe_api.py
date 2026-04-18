from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from app.core.security import read_session
from app.services.recipe_service import (
    get_user_recipes,
    add_recipe_db,
    update_recipe_db,
    delete_recipe_db,
    get_user_role
)

router = APIRouter()


# ===========================
# GET USER RECIPES (JSON)
# ===========================
@router.get("/recipes")
async def get_recipes(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = read_session(session_id)

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    recipes = get_user_recipes(user_id)

    return {
        "success": True,
        "count": len(recipes),
        "data": recipes
    }


# ===========================
# ADD RECIPE (JSON)
# ===========================
@router.post("/recipes")
async def add_recipe(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    cook_time: int = Form(...),
    difficulty: str = Form(...),
    image: UploadFile = File(...),
    file: UploadFile = File(...)
):
    session_id = request.cookies.get("session_id")
    if session_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = read_session(session_id)

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if difficulty not in ["Easy", "Intermediate", "Hard"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")

    result = add_recipe_db(
        {
            "title": title,
            "description": description,
            "cook_time": cook_time,
            "difficulty": difficulty
        },
        image,
        file,
        user_id
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "success": True,
        "message": "Recipe created successfully"
    }


# ===========================
# UPDATE RECIPE (JSON)
# ===========================
@router.put("/recipes/{recipe_id}")
async def update_recipe(
    request: Request,
    recipe_id: int,
    title: str = Form(...),
    description: str = Form(...),
    cook_time: int = Form(...),
    difficulty: str = Form(...),
    image: UploadFile = File(None),
    file: UploadFile = File(None)
):
    session_id = request.cookies.get("session_id")
    if session_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = read_session(session_id)

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = update_recipe_db(
        recipe_id,
        {
            "title": title,
            "description": description,
            "cook_time": cook_time,
            "difficulty": difficulty
        },
        image,
        file,
        user_id
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "success": True,
        "message": "Recipe updated successfully"
    }


# ===========================
# DELETE RECIPE (JSON)
# ===========================
@router.delete("/recipes/{recipe_id}")
async def delete_recipe(request: Request, recipe_id: int):

    session_id = request.cookies.get("session_id")
    if session_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = read_session(session_id)

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    is_admin = False  # optionally fetch via service if needed

    result = delete_recipe_db(recipe_id, user_id, is_admin)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "success": True,
        "message": "Recipe deleted successfully"
    }
