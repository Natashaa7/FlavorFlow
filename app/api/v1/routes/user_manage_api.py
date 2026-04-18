from fastapi import APIRouter
from app.services.user_service import get_all_users, add_user, update_user, delete_user
from fastapi import HTTPException
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter(prefix="/user_manage", tags=["User Management"])


@router.get("/users")
async def get_users():
    users = get_all_users()

    return {
        "success": True,
        "message": "Users fetched successfully",
        "data": users
    }


@router.post("/users")
async def add_user_api(payload: UserCreate):
    """
    Expected payload:
    {
        "name": "",
        "username": "",
        "email": "",
        "phonenumber": "",
        "dob": "",
        "password": ""
    }
    """

    result = add_user(payload.dict())

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": result["error"]
            }
        )

    return {
        "success": True,
        "message": "User created successfully"
    }



@router.put("/users/{user_id}")
async def update_user_api(user_id: int, payload: UserUpdate):

    update_user(user_id, payload.dict())

    return {
        "success": True,
        "message": "User updated successfully",
        "user_id": user_id
    }


@router.delete("/users/{user_id}")
async def delete_user_api(user_id: int):

    delete_user(user_id)

    return {
        "success": True,
        "message": "User deleted successfully",
        "user_id": user_id
    }
