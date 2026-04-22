from fastapi import APIRouter, Request, Form, File, UploadFile, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.core.security import require_user
from app.services.recipe_service import (
    get_user_recipes,
    add_recipe_db,
    update_recipe_db,
    delete_recipe_db
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/share_recipe", response_class=HTMLResponse)
async def share_recipe(request: Request, user=Depends(require_user)):

    recipes = get_user_recipes(user["id"])

    return templates.TemplateResponse(
        "pages/admin_recipe.html" if user.get("is_admin") else "pages/share_recipe.html",
        {
            "request": request,
            "recipes": recipes,
            "user": user
        }
    )


@router.post("/add-recipe")
async def add_recipe(
    user=Depends(require_user),
    title: str = Form(...),
    description: str = Form(...),
    cook_time: int = Form(...),
    difficulty: str = Form(...),
    image: UploadFile = File(...),
    file: UploadFile = File(...)
):

    result = add_recipe_db(
        {
            "title": title,
            "description": description,
            "cook_time": cook_time,
            "difficulty": difficulty
        },
        image,
        file,
        user["id"]
    )

    if not result["success"]:
        return JSONResponse(result)

    redirect_url = "/admin/admin_recipe" if user.get("is_admin") else "/share_recipe"

    return JSONResponse({
        "success": True,
        "message": "Recipe created successfully",
        "redirect": redirect_url
    })

@router.post("/update-recipe")
async def update_recipe(
    user=Depends(require_user),
    id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    cook_time: int = Form(...),
    difficulty: str = Form(...),
    image: UploadFile = File(None),
    file: UploadFile = File(None)
):

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
        user["id"]
    )

    if not result["success"]:
        return JSONResponse(result)

    redirect_url = "/admin/admin_recipe" if user.get("is_admin") else "/share_recipe"

    return JSONResponse({
        "success": True,
        "message": "Recipe updated successfully",
        "redirect": redirect_url
    })

@router.post("/delete-recipe")
async def delete_recipe(
    user=Depends(require_user),
    id: int = Form(...)
):

    result = delete_recipe_db(id, user["id"], user.get("is_admin", False))

    if not result["success"]:
        return JSONResponse(result)

    redirect_url = "/admin/admin_recipe" if user.get("is_admin") else "/share_recipe"

    return JSONResponse({
        "success": True,
        "message": "Recipe deleted successfully",
        "redirect": redirect_url
    })
