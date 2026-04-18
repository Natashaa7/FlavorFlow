from pydantic import BaseModel, EmailStr, validator
from app.utils.validation import (
    validate_password, validate_phone, validate_email
)
from typing import Optional

class SignupForm(BaseModel):
    name: str
    username: str
    email: EmailStr
    phonenumber: str
    password: str
    confirm_password: str

    val_pw = validator("password", allow_reuse=True)(validate_password)
    val_ph = validator("phonenumber", allow_reuse=True)(validate_phone)
    val_email = validator("email", allow_reuse=True)(validate_email)

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserCreate(BaseModel):
    name: str
    username: str
    email: str
    phonenumber: str
    dob: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str]
    username: Optional[str]
    email: Optional[str]
    phonenumber: Optional[str]
    dob: Optional[str]
    password: Optional[str]