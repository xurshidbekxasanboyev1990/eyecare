"""
==============================================================================
EyeCare Backend - Doctor API Routes
==============================================================================
Doctor management, reviews, and appointment endpoints.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from math import radians, sin, cos, sqrt, atan2
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from loguru import logger

from app.core.database import get_db
from app.models.doctor import Doctor, DoctorReview, Appointment, AppointmentStatus
from app.models.user import User
from app.schemas.doctor import (
    DoctorCreate, DoctorUpdate, DoctorResponse, DoctorListResponse,
    ReviewCreate, ReviewResponse, ReviewListResponse,
    AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentListResponse
)
from app.schemas.common import PaginationParams
from app.api.deps import get_current_user, get_pagination, CurrentUser, CurrentAdmin


router = APIRouter()


# ==============================================================================
# Helper Functions
# ==============================================================================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


# ==============================================================================
# Doctor Listing
# ==============================================================================

@router.get(
    "",
    response_model=List[DoctorListResponse],
    summary="Get doctors list",
    description="Get list of active doctors with optional filters"
)
async def get_doctors(
    pagination: PaginationParams = Depends(get_pagination),
    city: Optional[str] = None,
    specialty: Optional[str] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lng: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: float = Query(default=50, ge=1, le=200),
    sort_by: str = Query(default="priority", pattern="^(priority|rating|distance|price)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of doctors:
    - Filter by city, specialty, rating
    - Support location-based search
    - Sort by priority, rating, distance, or price
    """
    # Build base query
    query = select(Doctor).where(Doctor.is_active == True)
    
    # Apply filters
    if city:
        query = query.where(Doctor.city.ilike(f"%{city}%"))
    
    if specialty:
        query = query.where(Doctor.specialty.ilike(f"%{specialty}%"))
    
    if min_rating:
        query = query.where(Doctor.rating >= min_rating)
    
    # Apply sorting
    if sort_by == "rating":
        query = query.order_by(Doctor.rating.desc())
    elif sort_by == "price":
        query = query.order_by(Doctor.consultation_price.asc().nullslast())
    else:
        query = query.order_by(Doctor.priority.desc(), Doctor.rating.desc())
    
    # Pagination
    query = query.offset(pagination.offset).limit(pagination.limit)
    
    result = await db.execute(query)
    doctors = result.scalars().all()
    
    # Calculate distances if location provided
    response_items = []
    for doctor in doctors:
        item = DoctorListResponse.model_validate(doctor)
        
        if lat and lng and doctor.latitude and doctor.longitude:
            item.distance_km = round(
                calculate_distance(lat, lng, doctor.latitude, doctor.longitude),
                1
            )
        
        response_items.append(item)
    
    # Sort by distance if requested and location provided
    if sort_by == "distance" and lat and lng:
        response_items.sort(key=lambda x: x.distance_km or float('inf'))
        
        # Filter by radius
        response_items = [d for d in response_items if d.distance_km and d.distance_km <= radius_km]
    
    return response_items


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    summary="Get doctor details",
    description="Get detailed information about a specific doctor"
)
async def get_doctor(
    doctor_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get doctor by ID"""
    result = await db.execute(
        select(Doctor).where(Doctor.id == doctor_id)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shifokor topilmadi"
        )
    
    return DoctorResponse.model_validate(doctor)


# ==============================================================================
# Reviews
# ==============================================================================

@router.get(
    "/{doctor_id}/reviews",
    response_model=ReviewListResponse,
    summary="Get doctor reviews",
    description="Get reviews for a specific doctor"
)
async def get_doctor_reviews(
    doctor_id: UUID,
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db)
):
    """Get reviews for a doctor"""
    # Check doctor exists
    result = await db.execute(
        select(Doctor).where(Doctor.id == doctor_id)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shifokor topilmadi"
        )
    
    # Get reviews
    query = select(DoctorReview).where(
        and_(
            DoctorReview.doctor_id == doctor_id,
            DoctorReview.is_approved == True
        )
    ).order_by(DoctorReview.created_at.desc())
    
    # Count
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0
    
    # Paginate
    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return ReviewListResponse(
        items=[ReviewResponse.model_validate(r) for r in reviews],
        total=total,
        average_rating=doctor.rating
    )


@router.post(
    "/{doctor_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add review",
    description="Add a review for a doctor"
)
async def add_review(
    doctor_id: UUID,
    data: ReviewCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Add a review for a doctor"""
    # Check doctor exists
    result = await db.execute(
        select(Doctor).where(Doctor.id == doctor_id)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shifokor topilmadi"
        )
    
    # Check if user already reviewed
    existing = await db.execute(
        select(DoctorReview).where(
            and_(
                DoctorReview.doctor_id == doctor_id,
                DoctorReview.user_id == user.id
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Siz allaqachon sharh qoldirgansiz"
        )
    
    # Create review
    review = DoctorReview(
        doctor_id=doctor_id,
        user_id=user.id,
        rating=data.rating,
        comment=data.comment,
        is_approved=False  # Requires moderation
    )
    
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    logger.info(f"⭐ New review for doctor {doctor_id}: {data.rating}/5")
    
    return ReviewResponse.model_validate(review)


# ==============================================================================
# Appointments
# ==============================================================================

@router.get(
    "/appointments",
    response_model=AppointmentListResponse,
    summary="Get appointments",
    description="Get user's appointments"
)
async def get_appointments(
    user: CurrentUser,
    pagination: PaginationParams = Depends(get_pagination),
    status_filter: Optional[AppointmentStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get user's appointments"""
    query = select(Appointment).where(Appointment.user_id == user.id)
    
    if status_filter:
        query = query.where(Appointment.status == status_filter)
    
    query = query.order_by(Appointment.scheduled_at.desc())
    
    # Count
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0
    
    # Paginate
    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    items = []
    for apt in appointments:
        item = AppointmentResponse.model_validate(apt)
        
        # Get doctor info
        doctor_result = await db.execute(
            select(Doctor).where(Doctor.id == apt.doctor_id)
        )
        doctor = doctor_result.scalar_one_or_none()
        if doctor:
            item.doctor_name = doctor.full_name
            item.doctor_clinic = doctor.clinic_name
            item.doctor_phone = doctor.phone
        
        items.append(item)
    
    return AppointmentListResponse(
        items=items,
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.post(
    "/appointments",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Book appointment",
    description="Book an appointment with a doctor"
)
async def create_appointment(
    data: AppointmentCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Book an appointment"""
    # Check doctor exists and is active
    result = await db.execute(
        select(Doctor).where(
            and_(
                Doctor.id == data.doctor_id,
                Doctor.is_active == True
            )
        )
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shifokor topilmadi yoki faol emas"
        )
    
    # Check for conflicting appointments
    conflict = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == data.doctor_id,
                Appointment.scheduled_at == data.scheduled_at,
                Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
            )
        )
    )
    if conflict.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu vaqtda shifokor band"
        )
    
    # Create appointment
    appointment = Appointment(
        user_id=user.id,
        doctor_id=data.doctor_id,
        session_id=data.session_id,
        scheduled_at=data.scheduled_at,
        duration_minutes=data.duration_minutes,
        user_notes=data.notes,
        status=AppointmentStatus.PENDING
    )
    
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    
    logger.info(f"📅 New appointment: {appointment.id} with doctor {doctor.full_name}")
    
    response = AppointmentResponse.model_validate(appointment)
    response.doctor_name = doctor.full_name
    response.doctor_clinic = doctor.clinic_name
    response.doctor_phone = doctor.phone
    
    return response


@router.get(
    "/appointments/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Get appointment details",
    description="Get details of a specific appointment"
)
async def get_appointment(
    appointment_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get appointment details"""
    result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.id == appointment_id,
                Appointment.user_id == user.id
            )
        )
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uchrashuv topilmadi"
        )
    
    response = AppointmentResponse.model_validate(appointment)
    
    # Get doctor info
    doctor_result = await db.execute(
        select(Doctor).where(Doctor.id == appointment.doctor_id)
    )
    doctor = doctor_result.scalar_one_or_none()
    if doctor:
        response.doctor_name = doctor.full_name
        response.doctor_clinic = doctor.clinic_name
        response.doctor_phone = doctor.phone
    
    return response


@router.patch(
    "/appointments/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Update appointment",
    description="Update an appointment"
)
async def update_appointment(
    appointment_id: UUID,
    data: AppointmentUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Update appointment"""
    result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.id == appointment_id,
                Appointment.user_id == user.id
            )
        )
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uchrashuv topilmadi"
        )
    
    # Can only update pending appointments
    if appointment.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu uchrashuvni o'zgartirib bo'lmaydi"
        )
    
    # Update fields
    if data.scheduled_at:
        appointment.scheduled_at = data.scheduled_at
    if data.duration_minutes:
        appointment.duration_minutes = data.duration_minutes
    if data.notes is not None:
        appointment.user_notes = data.notes
    if data.status:
        appointment.status = data.status
    
    await db.commit()
    await db.refresh(appointment)
    
    return AppointmentResponse.model_validate(appointment)


@router.delete(
    "/appointments/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel appointment",
    description="Cancel an appointment"
)
async def cancel_appointment(
    appointment_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Cancel appointment"""
    result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.id == appointment_id,
                Appointment.user_id == user.id
            )
        )
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uchrashuv topilmadi"
        )
    
    if appointment.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu uchrashuvni bekor qilib bo'lmaydi"
        )
    
    appointment.status = AppointmentStatus.CANCELLED
    await db.commit()
    
    logger.info(f"❌ Appointment cancelled: {appointment_id}")
