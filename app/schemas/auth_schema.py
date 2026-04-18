from pydantic import BaseModel, EmailStr

class ForgotPasswordSchema(BaseModel):
    email: EmailStr
