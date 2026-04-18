from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
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

def get_user_role(cur, user_id: int):
    cur.execute("SELECT is_admin FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    return user["is_admin"] if user else False


# ===========================
# SHARE RECIPE PAGE (GET)
# ===========================
@router.get("/share-recipe", response_class=HTMLResponse)
async def share_recipe(request: Request):

    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT id, title, description, image_path, file_path, cook_time, difficulty, created_at
            FROM recipe
            WHERE user_id=%s
            ORDER BY created_at DESC
        """, (user_id,))

        recipes = cur.fetchall()

        is_admin = get_user_role(cur, user_id)

        print("IS ADMIN:", is_admin)  # DEBUG

        return templates.TemplateResponse(
            "pages/admin_recipe.html" if is_admin else "pages/share-recipe.html",
            {
                "request": request,
                "recipes": recipes
            }
        )

    finally:
        cur.close()
        conn.close()



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
    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)

    if not user_id:
        return JSONResponse({"success": False, "redirect": "/"})

    if difficulty not in ["Easy", "Intermediate", "Hard"]:
        return JSONResponse({"success": False, "error": "Invalid difficulty level!"})

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        is_admin = get_user_role(cur, user_id)

        image_name = f"{uuid.uuid4()}_{image.filename}"
        file_name = f"{uuid.uuid4()}_{file.filename}"

        image_path = f"uploads/images/{image_name}"
        file_path = f"uploads/files/{file_name}"

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        cur.execute("""
            INSERT INTO recipe
            (title, description, image_path, file_path, cook_time, difficulty, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (title, description, "/" + image_path, "/" + file_path, cook_time, difficulty, user_id))

        conn.commit()

        return JSONResponse({
            "success": True,
            "message": "Recipe added successfully!",
            "redirect": "/share-recipe"
        })

    except Exception as e:
        conn.rollback()
        print("Error:", e)
        return JSONResponse({"success": False, "error": "Failed to add recipe"})

    finally:
        cur.close()
        conn.close()



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
        return JSONResponse({"success": False, "redirect": "/"})

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        is_admin = get_user_role(cur, user_id)

        fields = ["title=%s", "description=%s", "cook_time=%s", "difficulty=%s"]
        values = [title, description, cook_time, difficulty]

        if image and image.filename:
            image_name = f"{uuid.uuid4()}_{image.filename}"
            image_path = f"uploads/images/{image_name}"

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            fields.append("image_path=%s")
            values.append("/" + image_path)

        if file and file.filename:
            file_name = f"{uuid.uuid4()}_{file.filename}"
            file_path = f"uploads/files/{file_name}"

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            fields.append("file_path=%s")
            values.append("/" + file_path)

        values.extend([id, user_id])

        cur.execute(f"""
            UPDATE recipe
            SET {', '.join(fields)}
            WHERE id=%s AND user_id=%s
        """, values)

        conn.commit()

        return JSONResponse({
            "success": True,
            "message": "Recipe updated successfully!",
            "redirect": "/share-recipe"
        })

    except Exception as e:
        conn.rollback()
        print("Error:", e)
        return JSONResponse({"success": False, "error": "Failed to update recipe"})

    finally:
        cur.close()
        conn.close()


@router.post("/delete-recipe")
async def delete_recipe(request: Request, id: int = Form(...)):

    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)

    if not user_id:
        return JSONResponse({"success": False, "redirect": "/"})

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        is_admin = get_user_role(cur, user_id)

        if is_admin:
            cur.execute("DELETE FROM recipe WHERE id=%s", (id,))
        else:
            cur.execute("DELETE FROM recipe WHERE id=%s AND user_id=%s", (id, user_id))

        conn.commit()

        return JSONResponse({
            "success": True,
            "message": "Recipe deleted successfully!",
            "redirect": "/share-recipe"
        })

    except Exception as e:
        conn.rollback()
        print("Delete error:", e)

        return JSONResponse({
            "success": False,
            "error": "Failed to delete recipe!"
        })

    finally:
        cur.close()
        conn.close()
