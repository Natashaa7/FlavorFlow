from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.core.security import read_session
from app.db.session import get_db_connection
from app.services.profile_service import (
    get_profile_data,
    update_profile,
    delete_user
)
from PIL import Image, ImageOps, UnidentifiedImageError
from io import BytesIO
import os
from uuid import uuid4

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# -------------------------
# PROFILE PAGE
# -------------------------
@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):

    session_id = request.cookies.get("session_id")
    user_id = read_session(session_id) if session_id else None

    if not user_id:
        return RedirectResponse("/authenticate", status_code=303)

    data = get_profile_data(user_id)

    success = request.query_params.get("success")
    error = request.query_params.get("error")

    template = "pages/ad-profile.html" if data["is_admin"] else "pages/profile.html"

    return templates.TemplateResponse(template, {
        "request": request,
        **data,
        "success": success,
        "error": error
    })



# -------------------------
# UPDATE PROFILE
# -------------------------
@router.post("/upd-profile")
async def upd_profile(
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

    session_id = request.cookies.get("session_id")
    user_id = read_session(session_id) if session_id else None

    if not user_id:
        return RedirectResponse("/authenticate", status_code=303)

    result = update_profile(user_id, {
        "name": name,
        "username": username,
        "email": email,
        "phonenumber": phonenumber,
        "dob": dob,
        "current_password": current_password,
        "password": password,
        "confirm_password": confirm_password
    })

    if not result["success"]:
        return templates.TemplateResponse("pages/profile.html", {
            "request": request,
            "error": result["message"]
        })

    return RedirectResponse("/profile?success=Profile updated successfully", status_code=303)



# -------------------------
# UPLOAD IMAGE
# -------------------------
@router.post("/upload-profile-image")
async def upload_image(request: Request, image: UploadFile = File(...)):

    session_id = request.cookies.get("session_id")
    user_id = read_session(session_id) if session_id else None

    if not user_id:
        return JSONResponse({"success": False})

    try:
        contents = await image.read()
        img = Image.open(BytesIO(contents))
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((512, 512))

    except UnidentifiedImageError:
        return JSONResponse({"success": False, "message": "Invalid image"})

    upload_dir = "app/static/profile_images"
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid4().hex}.jpg"
    file_path = os.path.join(upload_dir, filename)

    img.save(file_path, "JPEG", quality=85)

    image_url = f"/static/profile_images/{filename}"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET profile_image=%s WHERE id=%s",
        (image_url, user_id)
    )
    conn.commit()
    cur.close()
    conn.close()

    return JSONResponse({"success": True, "image_url": image_url})


# -------------------------
# DELETE ACCOUNT
# -------------------------
@router.post("/delete-portfolio")
async def delete_account(request: Request):

    session_id = request.cookies.get("session_id")
    user_id = read_session(session_id) if session_id else None

    if not user_id:
        return JSONResponse({"success": False}, status_code=401)

    delete_user(user_id)

    response = JSONResponse({
        "success": True,
        "redirect": "/"
    })

    response.delete_cookie("session_id")
    return response
