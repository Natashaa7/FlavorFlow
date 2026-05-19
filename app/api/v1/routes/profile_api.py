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
from app.utils.validation import (
    validate_email,
    validate_phone,
    validate_password,
    validate_dob
)
from datetime import datetime
from fastapi import File, UploadFile

router = APIRouter()


# GET PROFILE (API)
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


# UPDATE PROFILE (API)
@router.post("/update")
async def update_profile_api(payload: dict, request: Request):

    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = read_session(session_id)

    # VALIDATION
    errors = []

    try:
        validate_email(payload.get("email", ""))
    except ValueError as e:
        errors.append(str(e))

    try:
        validate_phone(payload.get("phonenumber", ""))
    except ValueError as e:
        errors.append(str(e))

    try:
        dob = payload.get("dob")
        if dob:
            dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
            validate_dob(dob_date)

    except ValueError as e:
        errors.append(str(e))

    if payload.get("password"):
        try:
            validate_password(payload["password"])
        except ValueError as e:
            errors.append(str(e))

    if errors:
        raise HTTPException(status_code=422, detail=errors)

    result = update_profile(user_id, payload)

    if not result["success"]:
        errors = result.get("errors", [])
        errors = list(map(str, errors))

        raise HTTPException(
            status_code=409 if any("exists" in e.lower() for e in errors) else 422,
            detail=errors
        )

    # SUCCESS RESPONSE (THIS FIXES NULL ISSUE)
    return {
        "success": True,
        "message": "Profile updated successfully"
    }


# UPLOAD IMAGE (API)
@router.post("/upload-image")
async def upload_image_api(
    request: Request,
    image: UploadFile = File(...)
):

    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = read_session(session_id)

    img = process_image(image)  # 👈 pass UploadFile directly

    if not img:
        raise HTTPException(status_code=400, detail="Invalid image")

    url = save_profile_image(img)
    update_profile_image(user_id, url)

    return {
        "success": True,
        "message": "Profile image updated successfully",
        "image_url": url
    }



# DELETE ACCOUNT (API)
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

