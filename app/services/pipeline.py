import os
from typing import List
from app.services.cv_model import predict_ingredients
from app.services.nlp_model import generate_recipe

UPLOAD_FOLDER = "static/uploads"

async def process_request(user_ingredients: List[str], images: List[str]):
    image_ingredients = {}
    
    if images:
        for image_path in images:
            if not os.path.exists(image_path):
                print(f"File not found: {image_path}")
                continue

            detected = predict_ingredients(image_path)

            if isinstance(detected, dict):
                for key, val in detected.items():
                    image_ingredients[key] = image_ingredients.get(key, 0) + val

    # merge manual + detected
    all_ingredients = list(set(user_ingredients + list(image_ingredients.keys())))

    if not all_ingredients:
        return {"success": False, "error": "No ingredients provided"}

    recipe = generate_recipe(all_ingredients)

    return {
        "success": True,
        "ingredients": all_ingredients,
        "detected": image_ingredients,   
        "recipe": recipe
    }