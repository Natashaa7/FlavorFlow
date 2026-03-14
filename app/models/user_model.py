from pydantic import BaseModel, EmailStr, validator
from datetime import date
from app.utils.validation_utils import validate_password, validate_phone, validate_email, validate_dob

class SignupForm(BaseModel):
    name: str
    username: str
    email: EmailStr
    phonenumber: str
    dob: date
    password: str
    confirm_password: str

    val_pw = validator("password", allow_reuse=True)(validate_password)
    val_ph = validator("phonenumber", allow_reuse=True)(validate_phone)
    val_dob = validator("dob", allow_reuse=True)(validate_dob)
    val_email = validator("email", allow_reuse=True)(validate_email)

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
