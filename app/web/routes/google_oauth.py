from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.core.oauth import oauth
from app.services.oauth_service import get_or_create_google_user
from app.core.security import create_session

router = APIRouter()


# STEP 1: Redirect to Google
@router.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
        prompt="select_account"
    )


# STEP 2: Callback
@router.get("/auth/google/callback")
async def google_callback(request: Request):

    token = await oauth.google.authorize_access_token(request)

    resp = await oauth.google.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        token=token
    )

    user_info = resp.json()

    user = get_or_create_google_user(user_info)

    session_token = create_session(user["id"])

    redirect_url = (
        "/admin_dashboard?login=google_success"
        if user["is_admin"]
        else "/index?login=google_success"
    )

    response = RedirectResponse(url=redirect_url, status_code=303)
    response.set_cookie(
        key="session_id",
        value=session_token,
        httponly=True,
        samesite="lax",
        secure=False  # set True in production HTTPS
    )

    return response
