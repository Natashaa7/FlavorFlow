from fastapi import APIRouter, Response
from fastapi.responses import  RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

# Logout
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session_id")
    return RedirectResponse(url="/", status_code=303)