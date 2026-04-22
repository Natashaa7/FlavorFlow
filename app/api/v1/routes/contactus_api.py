from fastapi import APIRouter, HTTPException
from app.schemas.message_schema import MessageSchema
from app.services.contactus_service import save_message

router = APIRouter()


@router.post("/send-message")
def send_message(message: MessageSchema):

    success = save_message(message)

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to save message"
        )

    return {
        "success": True,
        "message": "Message sent successfully"
    }
