"""
==============================================================================
EyeCare Backend - Doctor Schemas
==============================================================================
Pydantic schemas for doctor-related API endpoints.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

from app.models.doctor import AppointmentStatus


# ==============================================================================
# Doctor Schemas
# ==============================================================================

class DoctorBase(BaseModel):
    """Base doctor schema"""
    full_name: str = Field(..., min_length=2, max_length=255)
    specialty: str = Field(default="Oftalmolog", max_length=100)
    experience: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    telegram: Optional[str] = Field(None, max_length=50)
    clinic_name: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    work_hours: Optional[str] = Field(None, max_length=100)
    work_days: Optional[str] = Field(None, max_length=50)
    consultation_price: Optional[int] = Field(None, ge=0)
    currency: str = Field(default="UZS", max_length=3)


class DoctorCreate(DoctorBase):
    """Create doctor request"""
    is_active: bool = True
    is_verified: bool = False
    priority: int = Field(default=0, ge=0)


class DoctorUpdate(BaseModel):
    """Update doctor request"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    specialty: Optional[str] = Field(None, max_length=100)
    experience: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    telegram: Optional[str] = Field(None, max_length=50)
    clinic_name: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    work_hours: Optional[str] = Field(None, max_length=100)
    work_days: Optional[str] = Field(None, max_length=50)
    consultation_price: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0)


class DoctorResponse(BaseModel):
    """Doctor response schema"""
    id: UUID
    full_name: str
    specialty: str
    experience: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    telegram: Optional[str]
    clinic_name: Optional[str]
    address: Optional[str]
    city: Optional[str]
    district: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    work_hours: Optional[str]
    work_days: Optional[str]
    consultation_price: Optional[int]
    currency: str
    rating: float
    review_count: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class DoctorListResponse(BaseModel):
    """Doctor list item response"""
    id: UUID
    full_name: str
    specialty: str
    experience: Optional[str]
    clinic_name: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    work_hours: Optional[str]
    rating: float
    review_count: int
    consultation_price: Optional[int]
    distance_km: Optional[float] = None
    
    model_config = {"from_attributes": True}


# ==============================================================================
# Review Schemas
# ==============================================================================

class ReviewCreate(BaseModel):
    """Create review request"""
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    """Review response schema"""
    id: UUID
    doctor_id: UUID
    user_id: Optional[UUID]
    rating: int
    comment: Optional[str]
    is_approved: bool
    created_at: datetime
    
    # User info (if available)
    user_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    """Review list response"""
    items: List[ReviewResponse]
    total: int
    average_rating: float


# ==============================================================================
# Appointment Schemas
# ==============================================================================

class AppointmentCreate(BaseModel):
    """Create appointment request"""
    doctor_id: UUID
    session_id: Optional[UUID] = None
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)
    notes: Optional[str] = Field(None, max_length=500)


class AppointmentUpdate(BaseModel):
    """Update appointment request"""
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=120)
    notes: Optional[str] = Field(None, max_length=500)
    status: Optional[AppointmentStatus] = None


class AppointmentResponse(BaseModel):
    """Appointment response schema"""
    id: UUID
    user_id: UUID
    doctor_id: UUID
    session_id: Optional[UUID]
    scheduled_at: datetime
    duration_minutes: int
    status: AppointmentStatus
    user_notes: Optional[str]
    doctor_notes: Optional[str]
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime
    
    # Related info
    doctor_name: Optional[str] = None
    doctor_clinic: Optional[str] = None
    doctor_phone: Optional[str] = None
    
    model_config = {"from_attributes": True}


class AppointmentListResponse(BaseModel):
    """Appointment list response"""
    items: List[AppointmentResponse]
    total: int
    page: int
    limit: int
