import os
import shutil
import datetime
import re
import json

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.db.session import get_db_connection
from app.services.pipeline import process_request
from app.core.security import require_user

router = APIRouter()

UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# MODEL
class IngredientToggle(BaseModel):
    ingredient_name: str
    action: str

# TOGGLE INGREDIENT (SESSION ONLY)
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
            WHERE user_id=%s AND ingredient_name=%s
        """, (user["id"], data.ingredient_name))

    conn.commit()
    return {"success": True}


# UPLOAD IMAGE 
@router.post("/images/upload")
async def upload_image(file: UploadFile = File(...), user=Depends(require_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    ext = file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else "jpg"
    filename = f"user_{user['id']}_{datetime.datetime.now().timestamp()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

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

    return {"success": True, "image_id": image_id, "url": image_url}


# DELETE IMAGE
@router.delete("/images/{id}")
async def delete_image(id: int, user=Depends(require_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT file_path FROM ingredient_images
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


# GENERATE RECIPE
@router.post("/generate")
async def generate_recipe_api(user=Depends(require_user)):
    conn = get_db_connection()
    cur = conn.cursor()


    cur.execute("""
        SELECT ingredient_name
        FROM selected_ingredients
        WHERE user_id=%s
    """, (user["id"],))
    ingredients = [r["ingredient_name"] for r in cur.fetchall()]

    cur.execute("""
        SELECT file_path, image_url
        FROM ingredient_images
        WHERE user_id=%s
    """, (user["id"],))
    image_rows = cur.fetchall()

    image_paths = [r["file_path"] for r in image_rows]
    image_urls = [r["image_url"] for r in image_rows]

    if not ingredients and not image_paths:
        return {"success": False, "error": "No data selected"}

    
    result = await process_request(ingredients, image_paths)

    if not result.get("success", True):
        raise HTTPException(status_code=400, detail=result.get("error"))

    raw_recipe = result.get("recipe", "")
    detected = result.get("detected", {})

    if not raw_recipe:
        raise HTTPException(status_code=500, detail="Empty recipe generated")

    
    title_match = re.search(r"Recipe Name:\s*(.+?)(?:Steps:|$)", raw_recipe, re.IGNORECASE)
    recipe_title = title_match.group(1).strip() if title_match else "Untitled Recipe"

    steps_match = re.search(r"Steps:\s*(.+?)(?:Nutrition:|$)", raw_recipe, re.IGNORECASE)
    recipe_steps = steps_match.group(1).strip() if steps_match else raw_recipe

    nutrition_match = re.search(r"Nutrition:\s*(.+)", raw_recipe, re.IGNORECASE)

    nutrition = {}
    if nutrition_match:
        pairs = re.findall(r"(\w+):\s*([\d\.]+%?)", nutrition_match.group(1))
        nutrition = {k.capitalize(): v for k, v in pairs}

    
    cur.execute("""
        INSERT INTO generated_recipes
        (user_id, recipe_title, recipe_text,
         ingredients_used, detected_ingredients,
         nutrition, uploaded_images)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        user["id"],
        recipe_title,
        recipe_steps,
        json.dumps(ingredients),
        json.dumps(detected),
        json.dumps(nutrition),
        json.dumps(image_urls)
    ))

    
    # clear selected ingredients 
    cur.execute("""
        DELETE FROM selected_ingredients
        WHERE user_id=%s
    """, (user["id"],))

    # clear uploaded images 
    cur.execute("""
        DELETE FROM ingredient_images
        WHERE user_id=%s
    """, (user["id"],))

    conn.commit()

    return {
        "success": True,
        "data": {
            "title": recipe_title,
            "recipe": recipe_steps,
            "ingredients": ingredients,
            "detected": detected,
            "nutrition": nutrition,
            "images": image_urls
        }
    }


@router.get("/history")
async def get_history(user=Depends(require_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM generated_recipes
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (user["id"],))

    rows = cur.fetchall()

    def safe(v):
        if v is None:
            return {}
        if isinstance(v, (dict, list)):
            return v
        try:
            return json.loads(v)
        except:
            return {}

    return [
        {
            "id": r["id"],
            "title": r["recipe_title"],
            "recipe": r["recipe_text"],
            "ingredients": safe(r["ingredients_used"]),
            "detected": safe(r["detected_ingredients"]),
            "nutrition": safe(r["nutrition"]),
            "images": safe(r["uploaded_images"]),
            "created_at": r["created_at"].isoformat()
        }
        for r in rows
    ]


# DELETE HISTORY
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