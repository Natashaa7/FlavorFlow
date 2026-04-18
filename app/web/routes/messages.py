from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.message_service import get_all_messages, delete_message
from app.core.security import require_admin

router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(require_admin)]  # 🔒 FULL ADMIN PROTECTION
)

templates = Jinja2Templates(directory="app/templates")


# -------------------------
# VIEW MESSAGES (ADMIN ONLY)
# -------------------------
@router.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request):

    messages = get_all_messages()

    return templates.TemplateResponse(
        "pages/messages.html",
        {
            "request": request,
            "messages": messages
        }
    )


# -------------------------
# DELETE MESSAGE (ADMIN ONLY)
# -------------------------
@router.post("/delete-message")
async def delete_message_web(id: int = Form(...)):

    delete_message(id)

    return RedirectResponse(
        "/admin/messages?success=deleted",
        status_code=303
    )
