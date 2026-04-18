from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import JSONResponse
from app.services.pipeline import process_request

router = APIRouter()


@router.post("/generate")
async def generate_recipe_api(
    ingredients: list[str] = Form([]),
    image: UploadFile = File(None)
):
    result = await process_request(ingredients, image)

    if "error" in result:
        return JSONResponse(
            {"success": False, "error": result["error"]},
            status_code=400
        )

    return {
        "success": True,
        "data": result
    }
