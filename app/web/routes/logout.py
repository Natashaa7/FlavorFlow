from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/logout")
def logout():
    response = RedirectResponse(
        url="/authenticate?logout=success",
        status_code=302
    )
    response.delete_cookie("session_id", path="/")
    return response
