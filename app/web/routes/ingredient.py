from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.ingredient_service import (
    get_all_ingredients,
    create_ingredient,
    update_ingredient,
    delete_ingredient
)

from app.core.security import require_admin

router = APIRouter(
    prefix="/admin",  # 🔒 IMPORTANT: ADMIN AREA
    dependencies=[Depends(require_admin)]  # 🔒 BLOCK NON-ADMINS
)

templates = Jinja2Templates(directory="app/templates")


# -------------------------
# LIST PAGE (ADMIN ONLY)
# -------------------------
@router.get("/ingredients", response_class=HTMLResponse)
async def ingredients_page(request: Request):

    data = get_all_ingredients()

    return templates.TemplateResponse(
        "pages/ingredients.html",
        {
            "request": request,
            "ingredients": data
        }
    )


# -------------------------
# CREATE (ADMIN ONLY)
# -------------------------
@router.post("/ingredients/add")
async def add_ingredient_web(
    name: str = Form(...),
    quantity: str = Form(...),
    unit: str = Form(...)
):
    create_ingredient(name, quantity, unit)
    return RedirectResponse("/admin/ingredients", status_code=303)


# -------------------------
# UPDATE (ADMIN ONLY)
# -------------------------
@router.post("/ingredients/update/{id}")
async def update_ingredient_web(
    id: int,
    name: str = Form(...),
    quantity: str = Form(...),
    unit: str = Form(...)
):
    update_ingredient(id, name, quantity, unit)
    return RedirectResponse("/admin/ingredients", status_code=303)


# -------------------------
# DELETE (ADMIN ONLY)
# -------------------------
@router.get("/ingredients/delete/{id}")
async def delete_ingredient_web(id: int):
    delete_ingredient(id)
    return RedirectResponse("/admin/ingredients", status_code=303)
