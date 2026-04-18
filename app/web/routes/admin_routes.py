from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.security import require_admin, require_user

router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(require_admin)]   # 🔒 GLOBAL ADMIN PROTECTION
)

templates = Jinja2Templates(directory="templates")
