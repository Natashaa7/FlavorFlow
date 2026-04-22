import os
import shutil
import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.db.session import get_db_connection
from app.services.pipeline import process_request
from app.core.security import require_user

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class IngredientToggle(BaseModel):
    ingredient_name: str
    action: str


# -------------------------
# 1. Toggle Ingredients
# -------------------------
@router.post("/ingredients/toggle")
async def toggle_ingredient(data: IngredientToggle, user=Depends(require_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    if data.action == "add":
        cur.execute("""
            INSERT INTO selected_ingredients (user_id, ingredient_name)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (user["id"], data.ingredient_name))
    else:
        cur.execute("""
            DELETE FROM selected_ingredients
            WHERE user_id = %s AND ingredient_name = %s
        """, (user["id"], data.ingredient_name))

    conn.commit()
    return {"success": True}


# -------------------------
# 2. Upload Image
# -------------------------
@router.post("/images/upload")
async def upload_image(file: UploadFile = File(...), user=Depends(require_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    ext = file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else "jpg"
    filename = f"user_{user['id']}_{datetime.datetime.now().timestamp()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = f"/static/uploads/{filename}"

    cur.execute("""
        INSERT INTO ingredient_images (user_id, file_path, image_url)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (user["id"], file_path, image_url))

    row = cur.fetchone()
    image_id = row["id"] if isinstance(row, dict) else row[0]

    conn.commit()

    return {
        "success": True,
        "image_id": image_id,
        "url": image_url
    }


# -------------------------
# 3. Delete Image
# -------------------------
@router.delete("/images/{id}")
async def delete_image(id: int, user=Depends(require_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT file_path
        FROM ingredient_images
        WHERE id=%s AND user_id=%s
    """, (id, user["id"]))

    row = cur.fetchone()

    if not row:
        return {"success": False}

    file_path = row["file_path"] if isinstance(row, dict) else row[0]

    if os.path.exists(file_path):
        os.remove(file_path)

    cur.execute("""
        DELETE FROM ingredient_images
        WHERE id=%s AND user_id=%s
    """, (id, user["id"]))

    conn.commit()

    return {"success": True}


# -------------------------
# 4. Generate Recipe
# -------------------------
@router.post("/generate")
async def generate_recipe_api(user=Depends(require_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    # Get ingredients
    cur.execute("""
        SELECT ingredient_name
        FROM selected_ingredients
        WHERE user_id=%s
    """, (user["id"],))

    ingredients = [r["ingredient_name"] for r in cur.fetchall()]

    # Get image FILE PATHS (IMPORTANT for YOLO)
    cur.execute("""
        SELECT file_path
        FROM ingredient_images
        WHERE user_id=%s
    """, (user["id"],))

    images = [r["file_path"] for r in cur.fetchall()]

    if not ingredients and not images:
        return {"success": False, "error": "No data selected"}

    result = await process_request(ingredients, images)

    # Safety check (prevents KeyError crash)
    if not result.get("success", True):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Recipe generation failed")
        )

    recipe_text = result.get("recipe", "")

    if not recipe_text:
        raise HTTPException(status_code=500, detail="Empty recipe generated")

    cur.execute("""
        INSERT INTO generated_recipes
        (user_id, recipe_title, recipe_text, ingredients_used)
        VALUES (%s, %s, %s, %s)
    """, (
        user["id"],
        result.get("title", "New Recipe"),
        recipe_text,
        ", ".join(ingredients)
    ))

    # Clear temp state
    cur.execute("DELETE FROM selected_ingredients WHERE user_id=%s", (user["id"],))
    cur.execute("DELETE FROM ingredient_images WHERE user_id=%s", (user["id"],))

    conn.commit()

    return {
        "success": True,
        "data": {
            "recipe": recipe_text,
            "ingredients": ingredients,
            "detected": result.get("detected", {})   # 👈 ADD THIS LINE
        }
    }


# -------------------------
# 5. History
# -------------------------
@router.get("/history")
async def get_history(user=Depends(require_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, recipe_title, recipe_text, ingredients_used, created_at
        FROM generated_recipes
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (user["id"],))

    rows = cur.fetchall()

    return [
        {
            "id": r["id"],
            "title": r["recipe_title"],
            "recipe": r["recipe_text"],
            "ingredients": r["ingredients_used"],
            "created_at": r["created_at"].isoformat()
        }
        for r in rows
    ]


# -------------------------
# 6. Delete History
# -------------------------
@router.delete("/history/{id}")
async def delete_history(id: int, user=Depends(require_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM generated_recipes
        WHERE id=%s AND user_id=%s
    """, (id, user["id"]))

    conn.commit()

    return {"success": True}