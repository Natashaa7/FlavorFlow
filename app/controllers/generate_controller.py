from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.pipeline import process_request
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

@router.get("/generate-recipe", response_class=HTMLResponse)
async def generate_recipe(request: Request):
    return templates.TemplateResponse("pages/generate-recipe.html", {"request": request})


@router.post("/generate")
async def generate_recipe_api(
    ingredients: list[str] = Form([]),
    image: UploadFile = File(None)
):
    result = await process_request(ingredients, image)

    if "error" in result:
        return JSONResponse(result, status_code=400)

    return result