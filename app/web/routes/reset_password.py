from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.reset_pw_service import verify_reset_code, reset_user_password
from app.core.security import create_session

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("pages/reset_password.html", {
        "request": request
    })


@router.post("/reset-password")
async def reset_password(
    request: Request,
    email: str = Form(...),
    code: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "pages/reset_password.html",
            {"request": request, "errors": ["Passwords do not match"]},
            status_code=400,
        )

    user, error = verify_reset_code(email, code)

    if error:
        return templates.TemplateResponse(
            "pages/reset_password.html",
            {"request": request, "errors": [error]},
            status_code=400,
        )

    try:
        reset_user_password(email, new_password)
    except ValueError as e:
        return templates.TemplateResponse(
            "pages/reset_password.html",
            {"request": request, "errors": [str(e)]},
            status_code=400,
        )

    session_token = create_session(user["id"])

    response = RedirectResponse("/index?login=reset_success", status_code=303)
    response.set_cookie("session_id", session_token, httponly=True)
    return response
