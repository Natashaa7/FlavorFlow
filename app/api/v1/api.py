from fastapi import APIRouter
from app.api.v1.routes import admin_dashboard_api, authentication_api, contactus_api, cookbook_api, forgot_password_api, generate_recipe_api, index_api, ingredient_api, logout_api, messages_api, profile_api, reset_password_api, share_recipe_api, user_manage_api, view_recipe_api
from app.api.v1.routes.generate_recipe_api import router as generate_recipe_router

api_router = APIRouter()

api_router.include_router(admin_dashboard_api.router, tags=["Admin Dashboard"])
api_router.include_router(authentication_api.router, prefix="/authentication", tags=["Authentication"])
api_router.include_router(contactus_api.router, prefix="/contactus", tags=["Contact Us"])
api_router.include_router(cookbook_api.router, prefix="/cookbook", tags=["Cookbook"])
api_router.include_router(forgot_password_api.router, prefix="/forgot-password", tags=["Forgot Password"])
api_router.include_router(
    generate_recipe_router,
    prefix="/generate-recipe",
    tags=["Recipe"]
)
api_router.include_router(index_api.router, prefix="/index", tags=["Index"])
api_router.include_router(ingredient_api.router, prefix="/ingredients", tags=["Ingredients"])
api_router.include_router(logout_api.router, prefix="/logout", tags=["Logout"])
api_router.include_router(messages_api.router, prefix="/messages", tags=["Messages"])
api_router.include_router(profile_api.router, prefix="/profile", tags=["Profile"])
api_router.include_router(reset_password_api.router, prefix="/reset-password", tags=["Reset Password"])
api_router.include_router(share_recipe_api.router, prefix="/share_recipe", tags=["Share Recipe"])
api_router.include_router(user_manage_api.router, prefix="/user_manage", tags=["User Management"])
api_router.include_router(view_recipe_api.router, prefix="/view-recipes", tags=["View Recipes"])

