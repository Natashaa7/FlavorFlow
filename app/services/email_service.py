import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

def send_reset_email(to_email: str, code: str):
    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_PASSWORD")

    if sender_email is None or app_password is None:
        raise EnvironmentError("EMAIL_ADDRESS and EMAIL_PASSWORD must be set")

    subject = "FlavorFlow Password Reset Code"
    body = f"Your password reset code is: {code}\nIt expires in 10 minutes."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)
