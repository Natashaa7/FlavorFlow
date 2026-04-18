from fastapi import APIRouter, HTTPException
from app.services.ingredient_service import *

router = APIRouter()


# CREATE
@router.post("/")
async def add_ingredient(name: str, quantity: str, unit: str):
    return create_ingredient(name, quantity, unit)


# READ ALL
@router.get("/")
async def list_ingredients():
    return get_all_ingredients()


# READ ONE
@router.get("/{ingredient_id}")
async def get_one(ingredient_id: int):
    data = get_ingredient_by_id(ingredient_id)
    if not data:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return data


# UPDATE
@router.put("/{ingredient_id}")
async def edit_ingredient(ingredient_id: int, name: str, quantity: str, unit: str):
    updated = update_ingredient(ingredient_id, name, quantity, unit)

    if not updated:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    return updated


# DELETE
@router.delete("/{ingredient_id}")
async def remove_ingredient(ingredient_id: int):
    deleted = delete_ingredient(ingredient_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    return {"message": "Ingredient deleted successfully"}
