# app/services/pipeline.py
import os
from app.services.cv_model import predict_ingredients
from app.services.nlp_model import generate_recipe  # your text recipe generator

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def process_request(user_ingredients, image):
    image_ingredients = []

    if image:
        file_path = os.path.join(UPLOAD_FOLDER, image.filename)

        # Save uploaded image
        with open(file_path, "wb") as f:
            f.write(await image.read())

        # Predict ingredients from image
        image_ingredients = predict_ingredients(file_path)

    # Combine user input and detected ingredients
    all_ingredients = list(set(user_ingredients + image_ingredients))

    if not all_ingredients:
        return {"error": "No ingredients provided"}

    # Generate recipe using NLP model
    recipe = generate_recipe(all_ingredients)

    return {
        "ingredients": all_ingredients,
        "recipe": recipe
    }