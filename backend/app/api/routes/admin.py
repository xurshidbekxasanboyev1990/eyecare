"""
EyeCare Backend - Admin API Routes

Admin panel uchun API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import json

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_password_hash
from app.api.deps import get_current_admin
from app.models.user import User, Admin, UserRole
from app.models.test import TestSession, TestResult
from app.models.doctor import Doctor, Appointment
from app.models.telegram import TelegramSession
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationStatus
from app.schemas.common import SuccessResponse, PaginatedResponse

router = APIRouter()


# ==================== DASHBOARD ====================

@router.get("/dashboard")
async def get_dashboard_stats(
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin dashboard statistikasi
    """
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Users stats
    total_users = await db.scalar(select(func.count(User.id)))
    new_users_today = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= today_start)
    )
    new_users_week = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= week_ago)
    )
    active_users = await db.scalar(
        select(func.count(User.id)).where(User.is_active == True)
    )
    
    # Telegram users
    total_telegram_users = await db.scalar(select(func.count(TelegramSession.id)))
    active_telegram_users = await db.scalar(
        select(func.count(TelegramSession.id))
    )
    
    # Test sessions
    total_sessions = await db.scalar(select(func.count(TestSession.id)))
    sessions_today = await db.scalar(
        select(func.count(TestSession.id)).where(TestSession.created_at >= today_start)
    )
    completed_sessions = await db.scalar(
        select(func.count(TestSession.id)).where(TestSession.completed_at.isnot(None))
    )
    
    # Doctors
    total_doctors = await db.scalar(select(func.count(Doctor.id)))
    active_doctors = await db.scalar(
        select(func.count(Doctor.id)).where(Doctor.is_active == True)
    )
    
    # Appointments
    total_appointments = await db.scalar(select(func.count(Appointment.id)))
    pending_appointments = await db.scalar(
        select(func.count(Appointment.id)).where(Appointment.status == "pending")
    )
    
    # Test results by type
    result = await db.execute(
        select(TestResult.test_type, func.count(TestResult.id))
        .group_by(TestResult.test_type)
    )
    test_type_stats = {str(row[0].value): row[1] for row in result.all()}
    
    # Daily activity (last 7 days)
    daily_activity = []
    for i in range(7):
        day = today_start - timedelta(days=i)
        next_day = day + timedelta(days=1)
        
        users_count = await db.scalar(
            select(func.count(User.id)).where(
                and_(User.created_at >= day, User.created_at < next_day)
            )
        )
        sessions_count = await db.scalar(
            select(func.count(TestSession.id)).where(
                and_(TestSession.created_at >= day, TestSession.created_at < next_day)
            )
        )
        
        daily_activity.append({
            "date": day.strftime("%Y-%m-%d"),
            "users": users_count or 0,
            "sessions": sessions_count or 0
        })
    
    return {
        "users": {
            "total": total_users or 0,
            "new_today": new_users_today or 0,
            "new_week": new_users_week or 0,
            "active": active_users or 0
        },
        "telegram_users": {
            "total": total_telegram_users or 0,
            "active": active_telegram_users or 0
        },
        "test_sessions": {
            "total": total_sessions or 0,
            "today": sessions_today or 0,
            "completed": completed_sessions or 0,
            "completion_rate": round((completed_sessions or 0) / max(total_sessions or 1, 1) * 100, 2)
        },
        "doctors": {
            "total": total_doctors or 0,
            "active": active_doctors or 0
        },
        "appointments": {
            "total": total_appointments or 0,
            "pending": pending_appointments or 0
        },
        "test_type_stats": test_type_stats,
        "daily_activity": list(reversed(daily_activity))
    }


# ==================== USERS MANAGEMENT ====================

@router.get("/users", response_model=PaginatedResponse)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    role: Optional[UserRole] = None,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Foydalanuvchilar ro'yxati
    """
    query = select(User)
    
    # Filters
    if search:
        query = query.where(
            or_(
                User.full_name.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    if role:
        query = query.where(User.role == role)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Paginate
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return PaginatedResponse(
        items=[{
            "id": u.id,
            "phone": u.phone,
            "full_name": u.full_name,
            "email": u.email,
            "gender": u.gender.value if u.gender else None,
            "role": u.role.value if u.role else None,
            "is_active": u.is_active,
            "created_at": u.created_at
        } for u in users],
        total=total or 0,
        page=page,
        limit=page_size,
        total_pages=((total or 0) + page_size - 1) // page_size
    )


@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: str,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Foydalanuvchi batafsil ma'lumotlari
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )
    
    # Get test sessions
    result = await db.execute(
        select(TestSession)
        .where(TestSession.user_id == user_id)
        .order_by(TestSession.created_at.desc())
        .limit(10)
    )
    sessions = result.scalars().all()
    
    # Get telegram session if exists
    result = await db.execute(
        select(TelegramSession).where(TelegramSession.user_id == user_id)
    )
    telegram_session = result.scalar_one_or_none()
    
    return {
        "id": user.id,
        "phone": user.phone,
        "full_name": user.full_name,
        "email": user.email,
        "birth_date": user.birth_date,
        "gender": user.gender.value if user.gender else None,
        "role": user.role.value if user.role else None,
        "is_active": user.is_active,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "recent_sessions": [{
            "id": s.id,
            "created_at": s.created_at,
            "completed_at": s.completed_at,
            "source": s.source
        } for s in sessions],
        "telegram": {
            "telegram_id": telegram_session.telegram_id,
            "username": telegram_session.username,
            "first_name": telegram_session.first_name,
            "last_name": telegram_session.last_name
        } if telegram_session else None
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    data: dict,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Foydalanuvchi ma'lumotlarini yangilash
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )
    
    # Update allowed fields
    allowed_fields = ["full_name", "email", "is_active", "role"]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if "role" in update_data:
        update_data["role"] = UserRole(update_data["role"])
    
    await db.execute(
        update(User).where(User.id == user_id).values(**update_data)
    )
    await db.commit()
    
    return SuccessResponse(message="Foydalanuvchi yangilandi")


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Foydalanuvchini o'chirish (soft delete)
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )
    
    # Soft delete
    await db.execute(
        update(User).where(User.id == user_id).values(is_active=False)
    )
    await db.commit()
    
    return SuccessResponse(message="Foydalanuvchi o'chirildi")


# ==================== DOCTORS MANAGEMENT ====================

@router.get("/doctors", response_model=PaginatedResponse)
async def get_doctors_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Shifokorlar ro'yxati (Admin)
    """
    query = select(Doctor)
    
    if search:
        query = query.where(
            or_(
                Doctor.full_name.ilike(f"%{search}%"),
                Doctor.specialty.ilike(f"%{search}%")
            )
        )
    
    if is_active is not None:
        query = query.where(Doctor.is_active == is_active)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Paginate
    query = query.order_by(Doctor.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    doctors = result.scalars().all()
    
    return PaginatedResponse(
        items=[{
            "id": d.id,
            "full_name": d.full_name,
            "specialty": d.specialty,
            "phone": d.phone,
            "email": d.email,
            "rating": d.rating,
            "is_active": d.is_active,
            "created_at": d.created_at
        } for d in doctors],
        total=total or 0,
        page=page,
        limit=page_size,
        total_pages=((total or 0) + page_size - 1) // page_size
    )


@router.post("/doctors")
async def create_doctor(
    data: dict,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Yangi shifokor qo'shish
    """
    doctor = Doctor(
        full_name=data["full_name"],
        specialty=data.get("specialty", "Oftalmolog"),
        phone=data.get("phone"),
        email=data.get("email"),
        bio=data.get("bio"),
        experience=data.get("experience"),
        clinic_name=data.get("clinic_name"),
        address=data.get("address"),
        city=data.get("city"),
        work_hours=data.get("work_hours"),
        is_active=data.get("is_active", True)
    )
    
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    
    return {
        "id": doctor.id,
        "full_name": doctor.full_name,
        "message": "Shifokor muvaffaqiyatli qo'shildi"
    }


@router.put("/doctors/{doctor_id}")
async def update_doctor(
    doctor_id: str,
    data: dict,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Shifokor ma'lumotlarini yangilash
    """
    result = await db.execute(
        select(Doctor).where(Doctor.id == doctor_id)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shifokor topilmadi"
        )
    
    # Update allowed fields
    allowed_fields = [
        "full_name", "specialty", "phone", "email", "bio",
        "experience", "clinic_name", "address", "city", "work_hours",
        "is_active", "avatar_url", "consultation_price"
    ]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    await db.execute(
        update(Doctor).where(Doctor.id == doctor_id).values(**update_data)
    )
    await db.commit()
    
    return SuccessResponse(message="Shifokor yangilandi")


@router.delete("/doctors/{doctor_id}")
async def delete_doctor(
    doctor_id: str,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Shifokorni o'chirish
    """
    result = await db.execute(
        select(Doctor).where(Doctor.id == doctor_id)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shifokor topilmadi"
        )
    
    # Soft delete
    await db.execute(
        update(Doctor).where(Doctor.id == doctor_id).values(is_active=False)
    )
    await db.commit()
    
    return SuccessResponse(message="Shifokor o'chirildi")


# ==================== APPOINTMENTS ====================

@router.get("/appointments", response_model=PaginatedResponse)
async def get_appointments_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    doctor_id: Optional[int] = None,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Uchrashuvlar ro'yxati
    """
    query = select(Appointment).options(
        selectinload(Appointment.doctor)
    )
    
    if status_filter:
        query = query.where(Appointment.status == status_filter)
    
    if doctor_id:
        query = query.where(Appointment.doctor_id == doctor_id)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Paginate
    query = query.order_by(Appointment.scheduled_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    return PaginatedResponse(
        items=[{
            "id": a.id,
            "doctor": {
                "id": a.doctor.id,
                "full_name": a.doctor.full_name
            } if a.doctor else None,
            "scheduled_at": a.scheduled_at,
            "status": a.status.value,
            "user_notes": a.user_notes,
            "created_at": a.created_at
        } for a in appointments],
        total=total or 0,
        page=page,
        limit=page_size,
        total_pages=((total or 0) + page_size - 1) // page_size
    )


@router.put("/appointments/{appointment_id}")
async def update_appointment_status(
    appointment_id: str,
    data: dict,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Uchrashuv statusini yangilash
    """
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uchrashuv topilmadi"
        )
    
    if "status" in data:
        appointment.status = data["status"]
    if "notes" in data:
        appointment.user_notes = data["notes"]
    
    await db.commit()
    
    return SuccessResponse(message="Uchrashuv yangilandi")


# ==================== TEST SESSIONS ====================

@router.get("/test-sessions", response_model=PaginatedResponse)
async def get_test_sessions_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    completed_only: bool = False,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Test sessiyalari ro'yxati
    """
    query = select(TestSession)
    
    if user_id:
        query = query.where(TestSession.user_id == user_id)
    
    if completed_only:
        query = query.where(TestSession.completed_at.isnot(None))
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Paginate
    query = query.order_by(TestSession.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return PaginatedResponse(
        items=[{
            "id": s.id,
            "user_id": s.user_id,
            "created_at": s.created_at,
            "completed_at": s.completed_at,
            "source": s.source,
            "status": s.status.value if s.status else None,
            "overall_status": s.overall_status
        } for s in sessions],
        total=total or 0,
        page=page,
        limit=page_size,
        total_pages=((total or 0) + page_size - 1) // page_size
    )


@router.get("/test-sessions/{session_id}")
async def get_test_session_detail(
    session_id: str,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Test sessiyasi batafsil
    """
    result = await db.execute(
        select(TestSession)
        .options(
            selectinload(TestSession.results)
        )
        .where(TestSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessiya topilmadi"
        )
    
    return {
        "id": session.id,
        "user_id": session.user_id,
        "created_at": session.created_at,
        "completed_at": session.completed_at,
        "source": session.source,
        "status": session.status.value if session.status else None,
        "overall_status": session.overall_status,
        "concerns": session.concerns,
        "recommendations": session.recommendations,
        "results": [{
            "id": r.id,
            "test_type": r.test_type.value,
            "score": r.score,
            "status": r.status.value if r.status else None,
            "raw_data": r.raw_data,
            "created_at": r.created_at
        } for r in session.results]
    }


# ==================== TELEGRAM USERS ====================

@router.get("/telegram-users", response_model=PaginatedResponse)
async def get_telegram_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_blocked: Optional[bool] = None,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Telegram foydalanuvchilari ro'yxati
    """
    query = select(TelegramSession)
    
    if search:
        query = query.where(
            or_(
                TelegramSession.username.ilike(f"%{search}%"),
                TelegramSession.first_name.ilike(f"%{search}%"),
                TelegramSession.last_name.ilike(f"%{search}%")
            )
        )
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Paginate
    query = query.order_by(TelegramSession.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return PaginatedResponse(
        items=[{
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "language_code": u.language_code,
            "language": u.language,
            "created_at": u.created_at,
            "last_message_at": u.last_message_at
        } for u in users],
        total=total or 0,
        page=page,
        limit=page_size,
        total_pages=((total or 0) + page_size - 1) // page_size
    )


@router.put("/telegram-users/{telegram_user_id}/block")
async def block_telegram_user(
    telegram_user_id: str,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Telegram foydalanuvchisini bloklash
    """
    result = await db.execute(
        select(TelegramSession).where(TelegramSession.id == telegram_user_id)
    )
    tg_session = result.scalar_one_or_none()
    if not tg_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram foydalanuvchisi topilmadi"
        )
    # Block the linked user if exists
    if tg_session.user_id:
        await db.execute(
            update(User).where(User.id == tg_session.user_id).values(is_blocked=True)
        )
        await db.commit()
    
    return SuccessResponse(message="Foydalanuvchi bloklandi")


@router.put("/telegram-users/{telegram_user_id}/unblock")
async def unblock_telegram_user(
    telegram_user_id: str,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Telegram foydalanuvchisini blokdan chiqarish
    """
    result = await db.execute(
        select(TelegramSession).where(TelegramSession.id == telegram_user_id)
    )
    tg_session = result.scalar_one_or_none()
    if not tg_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram foydalanuvchisi topilmadi"
        )
    # Unblock the linked user if exists
    if tg_session.user_id:
        await db.execute(
            update(User).where(User.id == tg_session.user_id).values(is_blocked=False)
        )
        await db.commit()
    
    return SuccessResponse(message="Foydalanuvchi blokdan chiqarildi")


# ==================== NOTIFICATIONS ====================

@router.post("/notifications/send")
async def send_notification(
    data: dict,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Bildirishnoma yuborish
    """
    user_ids = data.get("user_ids", [])
    send_to_all = data.get("send_to_all", False)
    
    if send_to_all:
        result = await db.execute(select(User.id).where(User.is_active == True))
        user_ids = [row[0] for row in result.all()]
    
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Foydalanuvchilar tanlanmagan"
        )
    
    # Create notifications
    notifications = []
    for user_id in user_ids:
        notification = Notification(
            user_id=user_id,
            title=data["title"],
            body=data.get("message", data.get("body", "")),
            type=NotificationType(data.get("type", "system")),
            channel=NotificationChannel(data.get("channel", "push")),
            status=NotificationStatus.PENDING
        )
        notifications.append(notification)
    
    db.add_all(notifications)
    await db.commit()
    
    return {
        "message": f"{len(notifications)} ta bildirishnoma yuborildi",
        "count": len(notifications)
    }


# ==================== SETTINGS ====================

@router.get("/settings")
async def get_settings(
    admin: Admin = Depends(get_current_admin)
):
    """
    Tizim sozlamalarini olish
    """
    return {
        "app": {
            "name": settings.APP_NAME,
            "version": "1.0.0",
            "debug": settings.DEBUG
        },
        "telegram": {
            "bot_username": settings.TELEGRAM_BOT_USERNAME,
            "webapp_url": settings.TELEGRAM_WEBAPP_URL
        },
        "test_distances": {
            "snellen": settings.TEST_DISTANCE_SNELLEN,
            "ishihara": settings.TEST_DISTANCE_ISHIHARA,
            "astigmatism": settings.TEST_DISTANCE_ASTIGMATISM,
            "amsler": settings.TEST_DISTANCE_AMSLER
        }
    }


@router.put("/settings")
async def update_settings(
    data: dict,
    admin: Admin = Depends(get_current_admin)
):
    """
    Tizim sozlamalarini yangilash
    
    Note: Bu yerda settings faylga yozish yoki DB da saqlash kerak
    """
    # TODO: Implement settings persistence
    return SuccessResponse(message="Sozlamalar yangilandi")


# ==================== ADMINS MANAGEMENT ====================

@router.get("/admins")
async def get_admins(
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Adminlar ro'yxati
    """
    result = await db.execute(select(Admin))
    admins = result.scalars().all()
    
    return [{
        "id": a.id,
        "username": a.username,
        "full_name": a.full_name,
        "is_active": a.is_active,
        "created_at": a.created_at
    } for a in admins]


@router.post("/admins")
async def create_admin(
    data: dict,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Yangi admin qo'shish
    """
    # Check if username exists
    result = await db.execute(
        select(Admin).where(Admin.username == data["username"])
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu username band"
        )
    
    new_admin = Admin(
        username=data["username"],
        password_hash=get_password_hash(data["password"]),
        full_name=data.get("full_name", data["username"]),
        email=data.get("email", f"{data['username']}@eyecare.uz")
    )
    
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    
    return {
        "id": new_admin.id,
        "username": new_admin.username,
        "message": "Admin muvaffaqiyatli qo'shildi"
    }


@router.delete("/admins/{admin_id}")
async def delete_admin(
    admin_id: str,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Adminni o'chirish
    """
    if str(admin.id) == str(admin_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O'zingizni o'chira olmaysiz"
        )
    
    await db.execute(delete(Admin).where(Admin.id == admin_id))
    await db.commit()
    
    return SuccessResponse(message="Admin o'chirildi")
