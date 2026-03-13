"""
==============================================================================
EyeCare Backend - Doctor Model
==============================================================================
Doctor profiles and appointment management.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, Integer, DateTime, Text, Float,
    ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.core.database import Base


class AppointmentStatus(str, enum.Enum):
    """Appointment status enum"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Doctor(Base):
    """
    Doctor profile model.
    Stores information about recommended eye doctors.
    """
    __tablename__ = "doctors"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Basic Info ====
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), default="Oftalmolog")
    experience: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ==== Contact ====
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telegram: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # ==== Location ====
    clinic_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # ==== Schedule ====
    work_hours: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    work_days: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # ==== Pricing ====
    consultation_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="UZS")
    
    # ==== Rating ====
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # ==== Status ====
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    
    # ==== Timestamps ====
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # ==== Relationships ====
    reviews: Mapped[List["DoctorReview"]] = relationship(
        "DoctorReview",
        back_populates="doctor",
        lazy="selectin"
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="doctor",
        lazy="selectin"
    )
    
    # ==== Indexes ====
    __table_args__ = (
        Index("idx_doctors_city", "city"),
        Index("idx_doctors_is_active", "is_active"),
        Index("idx_doctors_rating", "rating"),
    )
    
    def __repr__(self) -> str:
        return f"<Doctor {self.full_name}>"
    
    def update_rating(self) -> None:
        """Recalculate average rating from reviews"""
        if self.reviews:
            total = sum(r.rating for r in self.reviews if r.is_approved)
            count = len([r for r in self.reviews if r.is_approved])
            if count > 0:
                self.rating = round(total / count, 1)
                self.review_count = count


class DoctorReview(Base):
    """
    Doctor review model.
    User reviews and ratings for doctors.
    """
    __tablename__ = "doctor_reviews"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Foreign Keys ====
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # ==== Review ====
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ==== Moderation ====
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # ==== Timestamps ====
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # ==== Relationships ====
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="reviews")
    
    def __repr__(self) -> str:
        return f"<DoctorReview {self.id}: {self.rating}/5>"


class Appointment(Base):
    """
    Appointment model.
    Schedules appointments between users and doctors.
    """
    __tablename__ = "appointments"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Foreign Keys ====
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("test_sessions.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # ==== Timing ====
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    
    # ==== Status ====
    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(AppointmentStatus),
        default=AppointmentStatus.PENDING
    )
    
    # ==== Notes ====
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doctor_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ==== Reminders ====
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # ==== Timestamps ====
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # ==== Relationships ====
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments")
    
    # ==== Indexes ====
    __table_args__ = (
        Index("idx_appointments_scheduled_at", "scheduled_at"),
        Index("idx_appointments_status", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Appointment {self.id}: {self.status.value}>"
