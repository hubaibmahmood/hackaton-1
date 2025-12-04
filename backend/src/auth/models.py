"""
Pydantic models for authentication.
Validates user registration and login data.
"""
import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    """User registration request model."""

    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength requirements.
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v


class UserLogin(BaseModel):
    """User login request model."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model (public data only)."""

    id: str
    email: str
    email_verified: bool
    status: str
    created_at: str
    last_login_at: Optional[str] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response model."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds
