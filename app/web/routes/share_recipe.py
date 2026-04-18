from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.core.security import read_session
from app.services.recipe_service import (
    get_user_recipes,
    add_recipe_db,
    update_recipe_db,
    delete_recipe_db
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ===========================
# SHARE PAGE (HTML ONLY)
# ===========================
@router.get("/share_recipe", response_class=HTMLResponse)
async def share_recipe(request: Request):

    session_id = request.cookies.get("session_id")
    if not session_id:
        return RedirectResponse("/", status_code=303)

    user_id = read_session(session_id)
    if not user_id:
        return RedirectResponse("/", status_code=303)

    recipes = get_user_recipes(user_id)

    return templates.TemplateResponse(
        "pages/share_recipe.html",
        {"request": request, "recipes": recipes}
    )


# ===========================
# ADD RECIPE (JSON FIXED)
# ===========================
@router.post("/add-recipe")
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
        return JSONResponse({"success": False, "error": "Not authenticated"})

    user_id = read_session(session_id)
    if not user_id:
        return JSONResponse({"success": False, "error": "Invalid session"})

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
        return JSONResponse(result)

    return JSONResponse({
        "success": True,
        "message": "Recipe created successfully",
        "redirect": "/share_recipe"
    })


# ===========================
# UPDATE RECIPE (JSON FIXED)
# ===========================
@router.post("/update-recipe")
async def update_recipe(
    request: Request,
    id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    cook_time: int = Form(...),
    difficulty: str = Form(...),
    image: UploadFile = File(None),
    file: UploadFile = File(None)
):

    session_id = request.cookies.get("session_id")
    if not session_id:
        return JSONResponse({"success": False, "error": "Not authenticated"})

    user_id = read_session(session_id)
    if not user_id:
        return JSONResponse({"success": False, "error": "Invalid session"})

    result = update_recipe_db(
        id,
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
        return JSONResponse(result)

    return JSONResponse({
        "success": True,
        "message": "Recipe updated successfully",
        "redirect": "/share_recipe"
    })


# ===========================
# DELETE RECIPE (FIXED)
# ===========================
@router.post("/delete-recipe")
async def delete_recipe(request: Request, id: int = Form(...)):

    session_id = request.cookies.get("session_id")
    if not session_id:
        return JSONResponse({"success": False, "error": "Not authenticated"})

    user_id = read_session(session_id)
    if not user_id:
        return JSONResponse({"success": False, "error": "Invalid session"})

    is_admin = False

    result = delete_recipe_db(id, user_id, is_admin)

    if not result["success"]:
        return JSONResponse(result)

    return JSONResponse({
        "success": True,
        "message": "Recipe deleted successfully",
        "redirect": "/share_recipe"
    })
