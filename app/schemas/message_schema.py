from pydantic import BaseModel, EmailStr

class MessageSchema(BaseModel):
    full_name: str
    email: EmailStr
    subject: str
    message: str
