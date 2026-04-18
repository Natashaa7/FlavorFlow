import re
from datetime import date

# Regex patterns
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{7,}$"
)
PHONE_PATTERN = re.compile(r"^9\d{9}$")
EMAIL_PATTERN = re.compile(r"^[^@]+@[^@]+\.com$")

def validate_password(password: str):
    """
    Password rules:
    - At least 7 characters
    - At least 1 uppercase
    - At least 1 lowercase
    - At least 1 number
    - At least 1 special character
    """
    if not PASSWORD_PATTERN.match(password):
        raise ValueError(
            "Password must be at least 7 chars, include uppercase, "
            "lowercase, number, and special character."
        )
    return password

def validate_phone(phonenumber: str):
    """
    Phone number must be exactly 10 digits
    """
    if not PHONE_PATTERN.match(phonenumber):
        raise ValueError("Phone number must start with '9' and be exactly 10 digits.")
    return phonenumber

def validate_email(email: str):
    """
    Email must contain '@' and end with '.com'
    """
    if not EMAIL_PATTERN.match(email):
        raise ValueError("Email must contain '@' and end with '.com'.")
    return email


def validate_dob(dob: date):
    """
    Validates that date of birth must be in the past
    """
    if dob >= date.today():
        raise ValueError("DOB must be in the past.")
    return dob