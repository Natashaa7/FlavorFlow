from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()  # Load EMAIL_ADDRESS and EMAIL_PASSWORD from .env

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# -----------------------------
# Helper: send reset code email
# -----------------------------
def send_reset_email(to_email, code):
    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_PASSWORD")

    subject = "FlavorFlow Password Reset Code"
    body = f"Your password reset code is: {code}\nIt expires in 10 minutes."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)

# -----------------------------
# GET: Show Forgot Password Page
# -----------------------------
@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("pages/forgot_password.html", {"request": request})

# -----------------------------
# POST: Handle Forgot Password
# -----------------------------
@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password(request: Request, email: str = Form(...)):

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Check if user exists
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        # Show error on forgot password page
        return templates.TemplateResponse(
            "pages/forgot_password.html",
            {"request": request, "error": "This email is not registered in the app."}
        )

    # Generate OTP and expiry
    code = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=10)

    # Save code in DB for that specific user
    cur.execute("""
        UPDATE users
        SET reset_code=%s,
            reset_code_expiry=%s
        WHERE email=%s
    """, (code, expiry, email))
    conn.commit()

    # Send email
    send_reset_email(email, code)
    print(f"Reset code sent to {email}: {code}")  # debug

    cur.close()
    conn.close()

    # Redirect to reset password page with email prefilled
    return RedirectResponse(url=f"/reset-password?email={email}", status_code=303)

