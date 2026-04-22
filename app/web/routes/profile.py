from fastapi import APIRouter, Request, Form, File, UploadFile, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.core.security import require_user
from app.db.session import get_db_connection
from app.services.profile_service import (
    get_profile_data,
    update_profile,
    delete_user
)
from datetime import datetime

from app.utils.validation import (
    validate_email,
    validate_phone,
    validate_password,
    validate_dob
)


from PIL import Image, ImageOps, UnidentifiedImageError
from io import BytesIO
import os
from uuid import uuid4

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, user=Depends(require_user)):

    data = get_profile_data(user["id"])

    success = request.query_params.get("success")
    error = request.query_params.get("error")

    template = "pages/ad-profile.html" if data["is_admin"] else "pages/profile.html"

    return templates.TemplateResponse(
        template,
        {
            "request": request,
            "user": user,
            **data,
            "success": success,
            "error": error
        }
    )

@router.post("/upd-profile")
async def upd_profile(
    user=Depends(require_user),
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phonenumber: str = Form(...),
    dob: str = Form(...),
    current_password: str = Form(None),
    password: str = Form(None),
    confirm_password: str = Form(None)
):

    try:
        # VALIDATION STEP
        validate_email(email)
        validate_phone(phonenumber)

        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
        validate_dob(dob_date)

        if password:
            validate_password(password)

    except ValueError as e:
        return templates.TemplateResponse(
            "pages/profile.html",
            {
                "request": {},
                "user": user,
                "error": str(e)
            }
        )

    result = update_profile(user["id"], {
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
        return templates.TemplateResponse(
            "pages/profile.html",
            {
                "request": {},
                "user": user,
                "errors": result["errors"]
            }
        )

    return RedirectResponse(
        "/profile?success=Profile updated successfully",
        status_code=303
    )


@router.post("/upload-profile-image")
async def upload_image(
    user=Depends(require_user),
    image: UploadFile = File(...)
):

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
        (image_url, user["id"])
    )
    conn.commit()
    cur.close()
    conn.close()

    return JSONResponse({
        "success": True,
        "image_url": image_url
    })

@router.post("/delete-portfolio")
async def delete_account(user=Depends(require_user)):

    delete_user(user["id"])

    response = JSONResponse({
        "success": True,
        "redirect": "/"
    })

    response.delete_cookie("session_id")
    return response
