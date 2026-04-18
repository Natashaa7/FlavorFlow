from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.contactus_service import save_message
from app.schemas.message_schema import MessageSchema
from app.core.security import require_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# -------------------------
# CONTACT PAGE (USER ONLY)
# -------------------------
@router.get("/contactus", response_class=HTMLResponse)
def contact_page(request: Request, user=Depends(require_user)):

    return templates.TemplateResponse(
        "pages/contactus.html",
        {
            "request": request,
            "user": user
        }
    )


# -------------------------
# SEND MESSAGE (USER ONLY)
# -------------------------
@router.post("/send-message")
def contact_submit(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    user=Depends(require_user)
):

    msg = MessageSchema(
        full_name=full_name,
        email=email,
        subject=subject,
        message=message
    )

    success = save_message(msg)

    if success:
        return RedirectResponse(
            url="/contactus?success=true",
            status_code=303
        )

    return RedirectResponse(
        url="/contactus?success=false",
        status_code=303
    )
