from pydantic import BaseModel

class Ingredient(BaseModel):
    name: str
    category: str
    usage_count: int