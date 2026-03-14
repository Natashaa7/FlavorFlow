from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
import bcrypt

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/reset_password", response_class=HTMLResponse)
def show_forgot_password_form(request: Request):
    return templates.TemplateResponse("pages/reset_password.html", {"request": request})

@router.post("/reset-password")
def reset_password(email: str = Form(...), code: str = Form(...), new_password: str = Form(...)):
    conn = get_db_connection()
    cur = conn.cursor()

    # Find user and valid code
    cur.execute("""
        SELECT pr.id, u.id 
        FROM password_reset pr
        JOIN users u ON pr.user_id = u.id
        WHERE u.email = %s AND pr.reset_code = %s AND pr.used = FALSE AND pr.expires_at > NOW()
    """, (email, code))
    
    record = cur.fetchone()
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    reset_id, user_id = record

    # Hash new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode()

    # Update user's password
    cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
    # Mark code as used
    cur.execute("UPDATE password_reset SET used = TRUE WHERE id = %s", (reset_id,))
    
    conn.commit()
    
    return {"message": "Password has been reset successfully."}
