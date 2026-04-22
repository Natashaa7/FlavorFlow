from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.security import require_admin
from app.services.user_service import (
    get_all_users,
    add_user,
    update_user,
    delete_user
)

router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(require_admin)]
)

templates = Jinja2Templates(directory="app/templates")


# =========================
# USER PAGE
# =========================
@router.get("/user_manage", response_class=HTMLResponse)
async def user_manage(request: Request):

    users = get_all_users()

    return templates.TemplateResponse(
        "pages/user_manage.html",
        {
            "request": request,
            "users": users
        }
    )


# =========================
# ADD USER
# =========================
@router.post("/add-users")
async def add_users(
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phonenumber: str = Form(...),
    dob: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):

    if password != confirm_password:
        return RedirectResponse("/admin/user_manage?error=password-mismatch", 303)

    result = add_user({
        "name": name,
        "username": username,
        "email": email,
        "phonenumber": phonenumber,
        "dob": dob,
        "password": password
    })

    if not result["success"]:
        return RedirectResponse(f"/admin/user_manage?error={result['error']}", 303)

    return RedirectResponse("/admin/user_manage?success=added", 303)


# =========================
# UPDATE USER
# =========================
@router.post("/update-users")
async def update_users(
    id: int = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    phonenumber: str = Form(...),
    name: str = Form(...),
    dob: str = Form(...)
):

    result = update_user(id, {
        "email": email,
        "username": username,
        "phonenumber": phonenumber,
        "name": name,
        "dob": dob
    })

    if not result.get("success", True):
        return RedirectResponse(f"/admin/user_manage?error={result['error']}", 303)

    return RedirectResponse("/admin/user_manage?success=updated", 303)


# =========================
# DELETE USER
# =========================
@router.post("/delete-users")
async def delete_users(id: int = Form(...)):

    result = delete_user(id)

    if not result.get("success", True):
        return RedirectResponse(f"/admin/user_manage?error={result['error']}", 303)

    return RedirectResponse("/admin/user_manage?success=deleted", 303)
