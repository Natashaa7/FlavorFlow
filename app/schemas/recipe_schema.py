from pydantic import BaseModel, Field

class RecipeSchema(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=5)
    cook_time: int = Field(gt=0, le=1000)
    difficulty: str
