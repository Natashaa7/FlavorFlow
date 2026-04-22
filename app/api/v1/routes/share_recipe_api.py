from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from app.core.security import read_session
from app.services.recipe_service import (
    get_user_recipes,
    add_recipe_db,
    update_recipe_db,
    delete_recipe_db,
    get_user_role
)
from app.schemas.recipe_schema import RecipeSchema
from app.utils.validation import validate_recipe

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
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = read_session(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    # ---------------- VALIDATION ----------------
    try:
        validate_recipe({
            "title": title,
            "description": description,
            "cook_time": cook_time,
            "difficulty": difficulty
        })
    except ValueError as e:
        raise HTTPException(status_code=422, detail=e.args[0])

    # ---------------- DB CALL ----------------
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
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = read_session(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    # ---------------- VALIDATION ----------------
    try:
        validate_recipe({
            "title": title,
            "description": description,
            "cook_time": cook_time,
            "difficulty": difficulty
        })
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # ---------------- UPDATE ----------------
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
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = read_session(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    is_admin = False

    result = delete_recipe_db(recipe_id, user_id, is_admin)

    if not result["success"]:
        error_msg = str(result.get("error") or "").lower()

        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=result.get("error"))

        if "unauthorized" in error_msg:
            raise HTTPException(status_code=403, detail=result.get("error"))

        raise HTTPException(status_code=500, detail=result.get("error"))

    return {
        "success": True,
        "message": "Recipe deleted successfully"
    }
