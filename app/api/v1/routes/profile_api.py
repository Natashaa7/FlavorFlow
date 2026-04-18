from fastapi import APIRouter, Request, HTTPException
from app.core.security import read_session
from app.services.profile_service import (
    get_profile_data,
    update_profile,
    delete_user
)
from app.services.image_service import (
    process_image,
    save_profile_image,
    update_profile_image
)

router = APIRouter()


# =========================
# GET PROFILE (API)
# =========================
@router.get("/")
async def get_profile_api(request: Request):

    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = read_session(session_id)

    return {
        "success": True,
        "data": get_profile_data(user_id)
    }



# =========================
# UPDATE PROFILE (API)
# =========================
@router.post("/update")
async def update_profile_api(payload: dict, request: Request):

    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = read_session(session_id)

    result = update_profile(user_id, payload)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return {
        "success": True,
        "message": "Profile updated"
    }


# =========================
# UPLOAD IMAGE (API)
# =========================
@router.post("/upload-image")
async def upload_image_api(request: Request, image: bytes):

    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = read_session(session_id)

    img = process_image(image)

    if not img:
        raise HTTPException(status_code=400, detail="Invalid image")

    url = save_profile_image(img)
    update_profile_image(user_id, url)

    return {
        "success": True,
        "image_url": url
    }


# =========================
# DELETE ACCOUNT (API)
# =========================
@router.delete("/")
async def delete_account_api(request: Request):

    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401)

    user_id = read_session(session_id)

    delete_user(user_id)

    return {
        "success": True,
        "message": "Account deleted"
    }

