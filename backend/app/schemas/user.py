"""
==============================================================================
EyeCare Backend - User Schemas
==============================================================================
Pydantic schemas for user-related API endpoints.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator
from uuid import UUID
import re

from app.models.user import Gender, UserRole


# ==============================================================================
# Base Schemas
# ==============================================================================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    full_name: str = Field(..., min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    language: str = Field(default="uz", pattern="^(uz|ru|en)$")


# ==============================================================================
# Authentication Schemas
# ==============================================================================

class UserRegister(BaseModel):
    """User registration request"""
    phone: str = Field(..., min_length=9, max_length=20)
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=6, max_length=100)
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate and normalize phone number"""
        # Remove all non-digit characters except +
        cleaned = re.sub(r"[^\d+]", "", v)
        
        # Ensure it starts with +998
        if not cleaned.startswith("+998"):
            if cleaned.startswith("998"):
                cleaned = "+" + cleaned
            elif cleaned.startswith("9") and len(cleaned) == 9:
                cleaned = "+998" + cleaned
            else:
                raise ValueError("Telefon raqami +998 bilan boshlanishi kerak")
        
        # Validate length
        if len(cleaned) != 13:  # +998XXXXXXXXX
            raise ValueError("Telefon raqami noto'g'ri formatda")
        
        return cleaned


class UserLogin(BaseModel):
    """User login request"""
    phone: str = Field(..., min_length=9, max_length=20)
    password: str = Field(..., min_length=1)
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[^\d+]", "", v)
        if not cleaned.startswith("+998"):
            if cleaned.startswith("998"):
                cleaned = "+" + cleaned
            elif cleaned.startswith("9") and len(cleaned) == 9:
                cleaned = "+998" + cleaned
        return cleaned


class TelegramLogin(BaseModel):
    """Telegram login request"""
    telegram_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class VerifyPhone(BaseModel):
    """Phone verification request"""
    phone: str
    code: str = Field(..., min_length=6, max_length=6)


class RefreshToken(BaseModel):
    """Token refresh request"""
    refresh_token: str


class PasswordReset(BaseModel):
    """Password reset request"""
    phone: str
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)


# ==============================================================================
# Token Schemas
# ==============================================================================

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str
    type: str
    exp: datetime
    iat: datetime


# ==============================================================================
# User Response Schemas
# ==============================================================================

class UserStats(BaseModel):
    """User statistics"""
    total_tests: int = 0
    last_test_date: Optional[datetime] = None
    tests_this_month: int = 0


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    telegram_id: Optional[int] = None
    full_name: str
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    avatar_url: Optional[str] = None
    language: str
    notifications_enabled: bool
    reminder_days: int
    is_verified: bool
    role: UserRole
    created_at: datetime
    stats: Optional[UserStats] = None
    
    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """User list response for admin"""
    id: UUID
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    telegram_id: Optional[int] = None
    full_name: str
    is_verified: bool
    is_active: bool
    is_blocked: bool
    login_count: int
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """User update request"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    language: Optional[str] = Field(None, pattern="^(uz|ru|en)$")
    notifications_enabled: Optional[bool] = None
    reminder_days: Optional[int] = Field(None, ge=30, le=365)


class ChangePassword(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


# ==============================================================================
# Admin Schemas
# ==============================================================================

class AdminLogin(BaseModel):
    """Admin login request"""
    username: str
    password: str
    two_factor_code: Optional[str] = None


class AdminCreate(BaseModel):
    """Admin creation request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    role: str = Field(default="admin", pattern="^(admin|moderator|super_admin)$")


class AdminResponse(BaseModel):
    """Admin response schema"""
    id: UUID
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    two_factor_enabled: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


# ==============================================================================
# Auth Response
# ==============================================================================

class AuthResponse(BaseModel):
    """Authentication response with user and tokens"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
