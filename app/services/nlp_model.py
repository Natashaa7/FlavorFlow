from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("app/model/twelve_model")
model = AutoModelForSeq2SeqLM.from_pretrained("app/model/twelve_model")

def generate_recipe(ingredients):
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

