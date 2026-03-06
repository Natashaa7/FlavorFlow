from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
import os, shutil

router = APIRouter()

# Templates folder
templates = Jinja2Templates(directory="app/templates")

# --- ensure folders exist ---
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/files", exist_ok=True)

@router.get("/share-recipe", response_class=HTMLResponse)
async def share_recipe(request: Request):
    return templates.TemplateResponse("pages/share-recipe.html", {"request": request})

@router.post("/add-recipe")
async def add_recipe(
    title: str = Form(...),
    description: str = Form(...),
    cook_time: int = Form(...),
    difficulty: str = Form(...),
    image: UploadFile = File(...),
    file: UploadFile = File(...)
):
    # --- basic validation ---
    if difficulty not in ["Easy", "Intermediate", "Hard"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty")

    # --- create unique filenames ---
    image_name = f"{uuid.uuid4()}_{os.path.basename(image.filename)}"
    file_name = f"{uuid.uuid4()}_{os.path.basename(file.filename)}"

    image_path = f"uploads/images/{image_name}"
    file_path = f"uploads/files/{file_name}"

    # --- save image ---
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    image.file.close()

    # --- save file ---
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file.file.close()

    # --- insert into database ---
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO recipe
            (title, description, image_path, file_path, cook_time, difficulty)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                title,
                description,
                "/" + image_path,  # optional leading slash
                "/" + file_path,
                cook_time,
                difficulty
            )
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        print("DB Error:", e)
        raise HTTPException(status_code=500, detail="Failed to add recipe")

    finally:
        cur.close()
        conn.close()

    # --- redirect back to share page with success ---
    return RedirectResponse(url="/share-recipe?success=1", status_code=303)

