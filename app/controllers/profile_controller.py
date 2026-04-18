from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.database.connection import get_db_connection
from app.utils.session_utils import read_session
from psycopg2.extras import RealDictCursor
import bcrypt
import os
from uuid import uuid4
from PIL import Image, UnidentifiedImageError, ImageOps
from io import BytesIO

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# =========================
# ROLE CHECK
# =========================
def get_user_role(cur, user_id: int):
    cur.execute("SELECT is_admin FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    return user["is_admin"] if user else False


# =========================
# PROFILE PAGE (GET)
# =========================
@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):

    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)

    if not session_token or not user_id:
        return RedirectResponse(url="/", status_code=303)

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # ROLE
        is_admin = get_user_role(cur, user_id)

        # RECIPE COUNT        
        cur.execute("""
            SELECT COUNT(*) AS recipes_count
            FROM recipe
            WHERE user_id=%s
        """, (user_id,))
        recipes_shared = cur.fetchone()["recipes_count"]

        # FAVORITES
        cur.execute("""
            SELECT COUNT(*) AS favorites_count
            FROM favorite
            WHERE user_id=%s
        """, (user_id,))
        favorites_count = cur.fetchone()["favorites_count"]


        # MOST LIKED
        cur.execute("""
            SELECT r.title, COUNT(f.id) AS like_count
            FROM recipe r
            JOIN favorite f ON r.id = f.recipe_id
            WHERE r.user_id=%s
            GROUP BY r.id
            ORDER BY like_count DESC
            LIMIT 1
        """, (user_id,))

        most_liked = cur.fetchone()

        if most_liked:
            most_liked_recipe_title = most_liked["title"]
            most_liked_recipe_count = most_liked["like_count"]
        else:
            most_liked_recipe_title = "No likes yet"
            most_liked_recipe_count = 0
        st_liked_recipe_count = 0

        # MOST VIEWED
        cur.execute("""
            SELECT title, views
            FROM recipe
            WHERE user_id=%s AND views > 0
            ORDER BY views DESC
            LIMIT 1
        """, (user_id,))

        most_viewed = cur.fetchone()

        if most_viewed:
            most_viewed_title = most_viewed["title"]
            most_viewed_views = most_viewed["views"]
        else:
            most_viewed_title = "No views yet"
            most_viewed_views = 0
        wed_views = most_viewed["views"] if most_viewed else 0

        # USER INFO
        cur.execute("""
            SELECT name, email, username, phonenumber, dob, created_at, profile_image
            FROM users WHERE id=%s
        """, (user_id,))
        user = cur.fetchone()

        template = "pages/ad-profile.html" if is_admin else "pages/profile.html"

        return templates.TemplateResponse(template, {
            "request": request,
            "user": user,
            "recipes_shared": recipes_shared,
            "favorites_count": favorites_count,
            "most_liked_recipe_title": most_liked_recipe_title,
            "most_liked_recipe_count": most_liked_recipe_count,
            "most_viewed_title": most_viewed_title,
            "most_viewed_views": most_viewed_views,
            "is_admin": is_admin
        })

    finally:
        cur.close()
        conn.close()


# =========================
# UPDATE PROFILE (POST)
# =========================
@router.post("/upd-profile")
async def update_profile(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phonenumber: str = Form(...),
    dob: str = Form(...),
    current_password: str = Form(None),
    password: str = Form(None),
    confirm_password: str = Form(None)
):

    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)

    if not session_token or not user_id:
        return JSONResponse({"success": False, "redirect": "/"})

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()

        if not user:
            return JSONResponse({"success": False, "redirect": "/"})

        stored_password = user["password"]

        # PASSWORD UPDATE
        if password:

            if not current_password:
                return JSONResponse({"success": False, "message": "Enter current password"})

            if not bcrypt.checkpw(current_password.encode(), stored_password.encode()):
                return JSONResponse({"success": False, "message": "Current password incorrect"})

            if password != confirm_password:
                return JSONResponse({"success": False, "message": "Passwords do not match"})

            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        else:
            hashed_password = stored_password

        # UPDATE USER
        cur.execute("""
            UPDATE users
            SET name=%s, username=%s, email=%s,
                phonenumber=%s, dob=%s, password=%s
            WHERE id=%s
        """, (name, username, email, phonenumber, dob, hashed_password, user_id))

        conn.commit()

        return JSONResponse({
            "success": True,
            "message": "Profile updated successfully",
            "redirect": "/profile"
        })

    finally:
        cur.close()
        conn.close()


# =========================
# UPLOAD PROFILE IMAGE
# =========================
@router.post("/upload-profile-image")
async def upload_profile_image(request: Request, image: UploadFile = File(...)):

    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)

    if not user_id:
        return JSONResponse({"success": False, "message": "Not authenticated"})

    try:
        contents = await image.read()
        if not contents:
            return JSONResponse({"success": False, "message": "Empty file"})

        img = Image.open(BytesIO(contents))
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((512, 512))

    except UnidentifiedImageError:
        return JSONResponse({"success": False, "message": "Invalid image"})
    except Exception:
        return JSONResponse({"success": False, "message": "Image processing failed"})

    upload_dir = "app/static/profile_images"
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid4().hex}.jpg"
    file_path = os.path.join(upload_dir, filename)

    img.save(file_path, "JPEG", quality=85)

    image_url = f"/static/profile_images/{filename}"

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE users SET profile_image=%s WHERE id=%s
        """, (image_url, user_id))
        conn.commit()

        return JSONResponse({
            "success": True,
            "image_url": image_url
        })

    finally:
        cur.close()
        conn.close()


# =========================
# DELETE ACCOUNT (SWEETALERT READY)
# =========================
@router.post("/delete-portfolio")
async def delete_portfolio(request: Request):

    session_token = request.cookies.get("session_id")
    user_id = read_session(session_token)

    if not user_id:
        return JSONResponse({"success": False, "message": "Not authenticated"}, status_code=401)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()

        response = JSONResponse({
            "success": True,
            "message": "Account deleted successfully",
            "redirect": "/"
        })

        response.delete_cookie("session_id")
        return response

    except Exception as e:
        conn.rollback()
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=500)

    finally:
        cur.close()
        conn.close()
