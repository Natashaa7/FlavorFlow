from fastapi import APIRouter, Request, HTTPException
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

    # ---------------- AUTH ----------------
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = read_session(session_token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    # ---------------- DELETE ----------------
    result = delete_message(message_id)

    # ---------------- ERROR HANDLING ----------------
    if not result.get("success"):

        error_msg = str(result.get("error") or "").lower()

        if "not found" in error_msg:
            raise HTTPException(
                status_code=404,
                detail="Message not found"
            )

        raise HTTPException(
            status_code=500,
            detail=result.get("error") or "Internal server error"
        )

    return {
        "success": True,
        "message": "Message deleted successfully"
    }


