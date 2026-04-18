from fastapi import APIRouter
from app.schemas.message_schema import MessageSchema
from app.services.contactus_service import save_message

router = APIRouter()


@router.post("/send-message")
def send_message(message: MessageSchema):

    success = save_message(message)

    if not success:
        return {"status": "error", "message": "Failed to save message"}

    return {"status": "success"}
