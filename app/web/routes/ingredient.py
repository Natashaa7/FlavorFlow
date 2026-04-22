from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.ingredient_service import (
    get_all_ingredients,
    create_ingredient,
    update_ingredient,
    delete_ingredient
)

from app.core.security import require_admin

router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(require_admin)]
)

templates = Jinja2Templates(directory="app/templates")


# -------------------------
# PAGE VIEW
# -------------------------
@router.get("/ingredient_manage", response_class=HTMLResponse)
async def ingredient_page(request: Request):

    data = get_all_ingredients()

    return templates.TemplateResponse(
        "pages/ingredient_manage.html",
        {
            "request": request,
            "ingredients": data
        }
    )


# -------------------------
# CREATE
# -------------------------
@router.post("/ingredient_manage/add")
async def add_ingredient_web(
    name: str = Form(...),
    category: str = Form(...),
    usage_count: int = Form(...)
):

    create_ingredient(name, category, usage_count)

    return JSONResponse({
        "success": True,
        "message": "Ingredient added successfully",
        "redirect": "/admin/ingredient_manage"
    })

# -------------------------
# UPDATE
# -------------------------
@router.post("/ingredient_manage/update/{id}")
async def update_ingredient_web(
    id: int,
    name: str = Form(...),
    category: str = Form(...),
    usage_count: int = Form(...)
):

    update_ingredient(id, name, category, usage_count)

    return JSONResponse({
        "success": True,
        "message": "Ingredient updated successfully",
        "redirect": "/admin/ingredient_manage"
    })


@router.post("/ingredient_manage/delete/{id}")
async def delete_ingredient_web(id: int):

    delete_ingredient(id)

    return JSONResponse({
        "success": True,
        "message": "Ingredient deleted successfully",
        "redirect": "/admin/ingredient_manage"
    })
