# app/services/nlp_model.py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("app/ml_models/nlp_model")
model = AutoModelForSeq2SeqLM.from_pretrained("app/ml_models/nlp_model")

def generate_recipe(ingredients):
    if not ingredients:
        return "No ingredients provided"

    prompt = f"""
You are a professional chef.

Create a recipe using:
{', '.join(ingredients)}

Include:
- Ingredients list
- Step-by-step instructions
- Cooking time
- Tips

Recipe:
"""

    inputs = tokenizer(prompt, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_length=300,
        temperature=0.8,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)