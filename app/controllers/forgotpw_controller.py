from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
import random
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def send_email(to_email: str, code: str):
    import smtplib
    from email.message import EmailMessage

    msg = EmailMessage()
    msg['Subject'] = 'Your Password'
    msg['From'] = 'email@gmail.com'
    msg['To'] = to_email
    msg.set_content(f'Your password reset code is: {code}')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('your_email@gmail.com', 'your_16_char_app_password')  # Use the App Password here
        smtp.send_message(msg)
    
@router.get("/forgot-password", response_class=HTMLResponse)
def show_forgot_password_form(request: Request):
    return templates.TemplateResponse("pages/forgot_password.html", {"request": request})

@router.post("/forgot-password")
def forgot_password(email: str = Form(...)):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if user exists
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Use this if RealDictCursor is used
    user_id = user["id"]
    code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Store code in DB
    cur.execute(
        "INSERT INTO password_reset (user_id, reset_code, expires_at) VALUES (%s, %s, %s)",
        (user_id, code, expires_at)
    )
    conn.commit()
    
    # Send code via email
    send_email(email, code)
    
    return {"message": "Password reset code sent to your email."}