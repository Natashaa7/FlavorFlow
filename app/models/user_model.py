from pydantic import BaseModel, EmailStr, validator
from datetime import date

class SignupForm(BaseModel):
    name: str
    username: str
    email: EmailStr
    phonenumber: str
    dob: date
    password: str
    confirm_password: str

    @validator('password')
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
