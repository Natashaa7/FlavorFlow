from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.security import read_session
from app.services.message_service import get_all_messages, delete_message

router = APIRouter(prefix="/messages", tags=["Messages"])


# -------------------------
# GET ALL MESSAGES
# -------------------------
@router.get("/")
def get_messages_api(request: Request):

    session_token = request.cookies.get("session_id")

    if not session_token:
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    user_id = read_session(session_token)

    if not user_id:
        return JSONResponse({"error": "invalid session"}, status_code=401)

    messages = get_all_messages()

    return {"status": "success", "messages": messages}


# -------------------------
# DELETE MESSAGE API
# -------------------------
@router.delete("/{message_id}")
def delete_message_api(message_id: int, request: Request):

    session_token = request.cookies.get("session_id")

    if not session_token:
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    user_id = read_session(session_token)

    if not user_id:
        return JSONResponse({"error": "invalid session"}, status_code=401)

    delete_message(message_id)

    return {
        "status": "success",
        "message": "Message deleted"
    }


""" from fastapi import APIRouter, HTTPException
from app.services.message_service import get_all_messages, delete_message
from app.core.security import read_session

router = APIRouter()


@router.get("/")
async def get_messages_api():
    return {
        "success": True,
        "data": get_all_messages()
    }


@router.delete("/{message_id}")
async def delete_message_api(message_id: int):
    delete_message(message_id)

    return {
        "success": True,
        "message": "Message deleted"
    }"""
