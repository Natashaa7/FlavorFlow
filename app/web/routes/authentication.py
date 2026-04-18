from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.schemas.user import SignupForm
from app.services.authentication_service import (
    create_user,
    authenticate_user,
    update_last_login,
)
from app.core.security import create_session

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# -------------------------
# AUTH PAGE
# -------------------------
@router.get("/authenticate", response_class=HTMLResponse)
async def authenticate_page(request: Request):
    return templates.TemplateResponse(
        "pages/authenticate.html",
        {"request": request, "active_form": "login"},
    )


# -------------------------
# SIGNUP
# -------------------------
@router.post("/signup")
async def signup(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phonenumber: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    try:
        form = SignupForm(
            name=name,
            username=username,
            email=email,
            phonenumber=phonenumber,
            password=password,
            confirm_password=confirm_password,
        )
    except ValidationError as e:
        errors = [err["msg"] for err in e.errors()]
        return templates.TemplateResponse(
            "pages/authenticate.html",
            {
                "request": request,
                "errors": errors,
                "active_form": "signup",
            },
            status_code=422,
        )

    result = create_user(form.dict())

    if not result["success"]:
        return templates.TemplateResponse(
            "pages/authenticate.html",
            {
                "request": request,
                "errors": [result["error"]],
                "active_form": "signup",
            },
        )

    return RedirectResponse(
        "/authenticate?success=account_created",
        status_code=303
    )


# -------------------------
# LOGIN
# -------------------------
@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user = authenticate_user(username, password)

    if not user:
        return templates.TemplateResponse(
            "pages/authenticate.html",
            {
                "request": request,
                "errors": ["Invalid username or password"],
                "active_form": "login",
            },
        )

    # update login time
    update_last_login(user["id"])

    # create session
    session_token = create_session(user["id"])

    # -------------------------
    # REDIRECT LOGIC (FIXED)
    # -------------------------
    if user.get("is_admin", False):
        redirect_url = "/admin/admin_dashboard"   # FIXED (matches router prefix)
    else:
        redirect_url = "/index"

    response = RedirectResponse(url=redirect_url, status_code=303)
    response.set_cookie(
        key="session_id",
        value=session_token,
        httponly=True,
        samesite="lax"
    )

    return response
