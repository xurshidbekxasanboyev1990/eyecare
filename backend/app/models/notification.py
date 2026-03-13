"""
==============================================================================
EyeCare Backend - Notification Model
==============================================================================
User notifications across multiple channels.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Boolean, Integer, DateTime, Text,
    ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification type enum"""
    REMINDER = "reminder"
    RESULT = "result"
    APPOINTMENT = "appointment"
    PROMOTION = "promotion"
    SYSTEM = "system"


class NotificationChannel(str, enum.Enum):
    """Notification delivery channel"""
    PUSH = "push"
    TELEGRAM = "telegram"
    SMS = "sms"
    EMAIL = "email"


class NotificationStatus(str, enum.Enum):
    """Notification status enum"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    """
    User notification model.
    Supports multiple channels: push, telegram, sms, email.
    """
    __tablename__ = "notifications"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Foreign Key ====
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # ==== Notification Content ====
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # ==== Delivery ====
    channel: Mapped[NotificationChannel] = mapped_column(
        SQLEnum(NotificationChannel),
        nullable=False
    )
    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus),
        default=NotificationStatus.PENDING
    )
    
    # ==== Timestamps ====
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # ==== Error Handling ====
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # ==== Timestamps ====
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # ==== Relationships ====
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    
    # ==== Indexes ====
    __table_args__ = (
        Index("idx_notifications_status", "status"),
        Index("idx_notifications_type", "type"),
        Index("idx_notifications_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Notification {self.id}: {self.type.value}>"


class AppSettings(Base):
    """
    Application settings model.
    Key-value storage for app configuration.
    """
    __tablename__ = "app_settings"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Key-Value ====
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # ==== Metadata ====
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # ==== Audit ====
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        return f"<AppSettings {self.key}>"


class ActivityLog(Base):
    """
    Activity log for audit trail.
    Tracks all important actions in the system.
    """
    __tablename__ = "activity_logs"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Actor ====
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)  # user, admin, system, bot
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # ==== Action ====
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # ==== Details ====
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ==== Timestamp ====
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # ==== Indexes ====
    __table_args__ = (
        Index("idx_activity_logs_actor", "actor_type", "actor_id"),
        Index("idx_activity_logs_action", "action"),
        Index("idx_activity_logs_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<ActivityLog {self.action}: {self.actor_type}>"
