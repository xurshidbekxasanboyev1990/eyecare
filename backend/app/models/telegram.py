"""
==============================================================================
EyeCare Backend - Telegram Bot Models
==============================================================================
Telegram session and bot state management.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Boolean, Integer, DateTime, Text, BigInteger,
    ForeignKey, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.core.database import Base


class TelegramSession(Base):
    """
    Telegram bot session model.
    Tracks user state and conversation flow.
    """
    __tablename__ = "telegram_sessions"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Telegram Info ====
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True
    )
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    # ==== User Link ====
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # ==== Profile ====
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    
    # ==== State ====
    current_state: Mapped[str] = mapped_column(String(50), default="idle")
    state_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # ==== Stats ====
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # ==== Preferences ====
    language: Mapped[str] = mapped_column(String(5), default="uz")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # ==== Timestamps ====
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # ==== Relationships ====
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="telegram_session"
    )
    
    def __repr__(self) -> str:
        return f"<TelegramSession {self.telegram_id}: {self.current_state}>"


class BotMessage(Base):
    """
    Bot message log for tracking conversations.
    Useful for analytics and debugging.
    """
    __tablename__ = "bot_messages"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Message Info ====
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # ==== Content ====
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # "in" or "out"
    content_type: Mapped[str] = mapped_column(String(20), default="text")  # text, photo, document
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # ==== Timestamps ====
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # ==== Indexes ====
    __table_args__ = (
        Index("idx_bot_messages_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<BotMessage {self.id}: {self.direction}>"
