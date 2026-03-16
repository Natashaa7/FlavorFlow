from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
from app.utils.session_utils import read_session
from psycopg2.extras import RealDictCursor
import os
import shutil
import uuid
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- ensure folders exist ---
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/files", exist_ok=True)


# ===========================
# SHARE RECIPE PAGE (GET)
# ===========================
@router.get("/share-recipe", response_class=HTMLResponse)
async def share_recipe(request: Request):
    # 🔹 read session like profile
    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)
    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    # fetch user recipes
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            """
            SELECT id, title, description, image_path, file_path, cook_time, difficulty, created_at
            FROM recipe
            WHERE user_id=%s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        recipes = cur.fetchall()
    except Exception as e:
        print("DB Error:", e)
        recipes = []
    finally:
        cur.close()
        conn.close()

    return templates.TemplateResponse(
        "pages/share-recipe.html",
        {"request": request, "recipes": recipes}
    )


# ===========================
# ADD RECIPE PAGE (POST)
# ===========================
@router.post("/add-recipe")
async def add_recipe(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    cook_time: int = Form(...),
    difficulty: str = Form(...),
    image: UploadFile = File(...),
    file: UploadFile = File(...)
):
    # 🔹 read session like profile
    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)
    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    # validate difficulty
    if difficulty not in ["Easy", "Intermediate", "Hard"]:
        return templates.TemplateResponse(
            "pages/share-recipe.html",
            {"request": request, "error": "Invalid difficulty level!"}
        )

    # create unique filenames
    image_name = f"{uuid.uuid4()}_{os.path.basename(image.filename)}"
    file_name = f"{uuid.uuid4()}_{os.path.basename(file.filename)}"
    image_path = f"uploads/images/{image_name}"
    file_path = f"uploads/files/{file_name}"

    # save files
    try:
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        print("File Save Error:", e)
        return templates.TemplateResponse(
            "pages/share-recipe.html",
            {"request": request, "error": "Failed to save uploaded files!"}
        )
    finally:
        image.file.close()
        file.file.close()

    # insert into DB
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO recipe
            (title, description, image_path, file_path, cook_time, difficulty, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (title, description, "/" + image_path, "/" + file_path, cook_time, difficulty, user_id)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("DB Error:", e)
        return templates.TemplateResponse(
            "pages/share-recipe.html",
            {"request": request, "error": "Failed to add recipe to database!"}
        )
    finally:
        cur.close()
        conn.close()

    # redirect back to GET page (like profile)
    return RedirectResponse(url="/share-recipe?success=1", status_code=303)


from typing import Optional

@router.post("/update-recipe")
async def update_recipe(
    request: Request,
    id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    cook_time: int = Form(...),
    difficulty: str = Form(...),
    image: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None)
):

    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)
    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    if difficulty not in ["Easy", "Intermediate", "Hard"]:
        return templates.TemplateResponse(
            "pages/share-recipe.html",
            {"request": request, "error": "Invalid difficulty level!"}
        )

    conn = get_db_connection()
    cur = conn.cursor()

    # 🔹 Base fields (always updated)
    fields = [
        "title=%s",
        "description=%s",
        "cook_time=%s",
        "difficulty=%s"
    ]
    values = [title, description, cook_time, difficulty]

    # =========================
    # IMAGE — only if uploaded
    # =========================
    if image and image.filename:

        image_name = f"{uuid.uuid4()}_{os.path.basename(image.filename)}"
        image_path = f"uploads/images/{image_name}"

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        fields.append("image_path=%s")
        values.append("/" + image_path)

    # =========================
    # FILE — only if uploaded
    # =========================
    if file and file.filename:

        file_name = f"{uuid.uuid4()}_{os.path.basename(file.filename)}"
        file_path = f"uploads/files/{file_name}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        fields.append("file_path=%s")
        values.append("/" + file_path)

    # WHERE clause
    values.extend([id, user_id])

    cur.execute(
        f"""
        UPDATE recipe
        SET {', '.join(fields)}
        WHERE id=%s AND user_id=%s
        """,
        values
    )

    conn.commit()
    cur.close()
    conn.close()

    return RedirectResponse(url="/share-recipe", status_code=303)

@router.post("/delete-recipe")
async def delete_recipe(
    request: Request,
    id: int = Form(...)
):
    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM recipe WHERE id=%s AND user_id=%s",
        (id, user_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return RedirectResponse(url="/share-recipe", status_code=303)

