from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class User(SQLModel, table=True):
    """User model for database"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=30)

    email: EmailStr = Field(unique=True, index=True)
    password_hash: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)

# Pydantic models for API requests/responses
class UserCreate(SQLModel):
    """Model for user registration"""
    email: EmailStr
    username: str = Field(min_length=3, max_length=30, regex="^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=8, max_length=100)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)

class UserLogin(SQLModel):
    """Model for user login"""
    username_or_email: str
    password: str

class UserResponse(SQLModel):
    """Model for user response (without password)"""
    id: int
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime

class UserUpdate(SQLModel):
    """Model for updating user profile"""
    username: Optional[str] = Field(None, min_length=3, max_length=30, regex="^[a-zA-Z0-9_-]+$")
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)


class PasswordChange(SQLModel):
    """Model for changing password"""
    old_password: str
    new_password: str = Field(min_length=8, max_length=70)


class DeleteAccount(SQLModel):
    """Model for account deletion confirmation"""
    password: str
    confirm: bool = Field(description="Must be true to confirm deletion")