from fastapi import APIRouter, Response
from fastapi.responses import  RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

# Logout
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/authenticate?logout=success", status_code=302)
    response.delete_cookie("session_id", path="/")
    return response


