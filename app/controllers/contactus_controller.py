from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.database.connection import get_db_connection

router = APIRouter()

class MessageSchema(BaseModel):
    full_name: str
    email: str
    subject: str
    message: str

@router.post("/send-message")
def send_message(message: MessageSchema):
    print(message)  # DEBUG

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO messages (full_name, email, subject, message)
        VALUES (%s, %s, %s, %s)
    """, (message.full_name, message.email, message.subject, message.message))

    conn.commit()
    cur.close()
    conn.close()

    return JSONResponse({"status": "success"})

