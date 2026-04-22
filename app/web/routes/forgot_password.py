from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.forgot_pw_service import create_reset_code
from app.services.email_service import send_reset_email

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# GET forgot password page
@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        "pages/forgot_password.html", {"request": request}
    )


# POST forgot password
@router.post("/forgot-password")
async def forgot_password(request: Request, email: str = Form(...)):

    # Check empty email manually
    if not email.strip():
        return templates.TemplateResponse(
            "pages/forgot_password.html",
            {"request": request, "error": "Email field cannot be empty."},
        )

    code = create_reset_code(email)

    if not code:
        return templates.TemplateResponse(
            "pages/forgot_password.html",
            {"request": request, "error": "This email is not registered."},
        )

    send_reset_email(email, code)

    return RedirectResponse(url=f"/reset-password?email={email}", status_code=303)
