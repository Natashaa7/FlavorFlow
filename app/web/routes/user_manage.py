from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.security import read_session
from app.services.user_service import (
    get_all_users, add_user, update_user, delete_user
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# =========================
# VIEW USERS
# =========================
@router.get("/user_manage", response_class=HTMLResponse)
async def user_manage(request: Request):
    users = get_all_users()

    return templates.TemplateResponse(
        "pages/user_manage.html",
        {"request": request, "users": users}
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
        return RedirectResponse("/user_manage?error=password-mismatch", 303)

    result = add_user({
        "name": name,
        "username": username,
        "email": email,
        "phonenumber": phonenumber,
        "dob": dob,
        "password": password
    })

    if not result["success"]:
        return RedirectResponse(f"/user_manage?error={result['error']}", 303)

    return RedirectResponse("/user_manage?success=added", 303)


# =========================
# UPDATE USER
# =========================
@router.post("/update-users")
async def update_users(
    request: Request,
    id: int = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    phonenumber: str = Form(...),
    name: str = Form(...),
    dob: str = Form(...),
    password: str = Form(None)
):

    session_token = request.cookies.get("session_id")
    if not read_session(session_token):
        return RedirectResponse("/", 303)

    update_user(id, {
        "email": email,
        "username": username,
        "phonenumber": phonenumber,
        "name": name,
        "dob": dob,
        "password": password
    })

    return RedirectResponse("/user_manage?success=updated", 303)


# =========================
# DELETE USER
# =========================
@router.post("/delete-users")
async def delete_users(request: Request, id: int = Form(...)):

    session_token = request.cookies.get("session_id")
    if not read_session(session_token):
        return RedirectResponse("/", 303)

    delete_user(id)

    return RedirectResponse("/user_manage?success=deleted", 303)
