from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/logout")
def logout_api():
    response = JSONResponse({
        "success": True,
        "message": "Logged out successfully"
    })

    response.delete_cookie("session_id", path="/")
    return response
