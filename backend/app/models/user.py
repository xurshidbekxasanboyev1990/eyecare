"""
==============================================================================
EyeCare Backend - User Model
==============================================================================
User database model with authentication and profile data.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, Integer, DateTime, Text, BigInteger,
    ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.core.database import Base


class Gender(str, enum.Enum):
    """User gender enum"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class UserRole(str, enum.Enum):
    """User role enum"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    """
    User model for authentication and profile management.
    Supports both phone and Telegram authentication.
    """
    __tablename__ = "users"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Authentication ====
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )
    telegram_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        unique=True,
        nullable=True,
        index=True
    )
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # ==== Profile ====
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    gender: Mapped[Optional[Gender]] = mapped_column(
        SQLEnum(Gender),
        nullable=True
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ==== Settings ====
    language: Mapped[str] = mapped_column(String(5), default="uz")
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Tashkent")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    reminder_days: Mapped[int] = mapped_column(Integer, default=180)
    
    # ==== Mobile/Push Notification ====
    fcm_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    device_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # ==== Verification ====
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_code: Mapped[Optional[str]] = mapped_column(String(6), nullable=True)
    verification_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    
    # ==== Role & Status ====
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ==== Login Stats ====
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    login_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    
    # ==== Timestamps ====
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # ==== Relationships ====
    test_sessions: Mapped[List["TestSession"]] = relationship(
        "TestSession",
        back_populates="user",
        lazy="selectin"
    )
    telegram_session: Mapped[Optional["TelegramSession"]] = relationship(
        "TelegramSession",
        back_populates="user",
        uselist=False
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        lazy="selectin"
    )
    
    # ==== Indexes ====
    __table_args__ = (
        Index("idx_users_created_at", "created_at"),
        Index("idx_users_is_active", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<User {self.id}: {self.full_name}>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    @property
    def display_name(self) -> str:
        """Get display name"""
        return self.full_name or self.phone or f"User {str(self.id)[:8]}"


class Admin(Base):
    """
    Admin model for admin panel access.
    Separate from regular users for enhanced security.
    """
    __tablename__ = "admins"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Credentials ====
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # ==== Role & Permissions ====
    role: Mapped[str] = mapped_column(String(20), default="admin")
    permissions: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # ==== Security ====
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # ==== Login Stats ====
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # ==== Timestamps ====
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        return f"<Admin {self.username}>"
