from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
from app.utils.session_utils import read_session
from psycopg2.extras import RealDictCursor

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

@router.get("/messages", response_class=HTMLResponse)
async def messages(request: Request):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)  

    cur.execute("""
        SELECT id, full_name, email, subject, message, created_at
        FROM messages
        ORDER BY created_at DESC
    """)

    messages = cur.fetchall()

    cur.close()
    conn.close()

    return templates.TemplateResponse(
        "pages/messages.html",
        {"request": request, "messages": messages}
    )

@router.post("/delete-message")
async def delete_message(
    request: Request,
    id: int = Form(...)
):
    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM messages WHERE id = %s",
        (id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    return RedirectResponse(url="/messages?success=deleted", status_code=303)

