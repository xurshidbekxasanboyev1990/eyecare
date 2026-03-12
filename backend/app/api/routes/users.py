"""
EyeCare Backend - Users API Routes

Foydalanuvchi profili va boshqaruvi
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from datetime import datetime
import uuid
import os

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_user, get_current_active_user
from app.models.user import User
from app.models.test import TestSession, TestResult
from app.models.notification import Notification
from app.schemas.user import UserResponse, UserUpdate, UserStats
from app.schemas.common import SuccessResponse, PaginatedResponse

# Alias
UserProfileResponse = UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Joriy foydalanuvchi profilini olish
    """
    # Get test statistics
    result = await db.execute(
        select(TestSession).where(TestSession.user_id == current_user.id)
    )
    test_sessions = result.scalars().all()
    
    total_tests = len(test_sessions)
    completed_tests = len([t for t in test_sessions if t.completed_at])
    
    user_stats = UserStats(
        total_tests=total_tests,
        last_test_date=max((t.completed_at for t in test_sessions if t.completed_at), default=None),
        tests_this_month=len([t for t in test_sessions if t.completed_at and t.completed_at.month == datetime.utcnow().month])
    )
    
    return UserResponse.model_validate(current_user, from_attributes=True).model_copy(
        update={"stats": user_stats}
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Joriy foydalanuvchi profilini yangilash
    """
    update_data = user_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yangilash uchun ma'lumot yo'q"
        )
    
    # Update user
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(**update_data)
    )
    await db.commit()
    
    # Refresh user
    await db.refresh(current_user)
    
    return current_user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Avatar rasmini yuklash
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faqat JPEG, PNG yoki WebP formatidagi rasmlar qabul qilinadi"
        )
    
    # Validate file size (max 5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rasm hajmi 5MB dan oshmasligi kerak"
        )
    
    # Generate unique filename
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    
    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
    os.makedirs(upload_dir, exist_ok=True)
    
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Update user avatar URL
    avatar_url = f"/uploads/avatars/{filename}"
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(avatar_url=avatar_url)
    )
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.delete("/me/avatar", response_model=SuccessResponse)
async def delete_avatar(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Avatar rasmini o'chirish
    """
    if current_user.avatar_url:
        # Delete file if exists
        filepath = os.path.join(settings.UPLOAD_DIR, current_user.avatar_url.lstrip("/uploads/"))
        if os.path.exists(filepath):
            os.remove(filepath)
    
    # Update user
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(avatar_url=None)
    )
    await db.commit()
    
    return SuccessResponse(message="Avatar muvaffaqiyatli o'chirildi")


@router.get("/me/notifications", response_model=PaginatedResponse)
async def get_user_notifications(
    page: int = 1,
    page_size: int = 20,
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Foydalanuvchi bildirishnomalarini olish
    """
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.where(Notification.read_at.is_(None))
    
    query = query.order_by(Notification.created_at.desc())
    
    # Count total
    count_result = await db.execute(
        select(Notification.id).where(Notification.user_id == current_user.id)
    )
    total = len(count_result.all())
    
    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return PaginatedResponse(
        items=[{
            "id": n.id,
            "title": n.title,
            "message": n.body,
            "type": n.type.value,
            "read_at": n.read_at,
            "created_at": n.created_at
        } for n in notifications],
        total=total,
        page=page,
        limit=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("/me/notifications/{notification_id}/read", response_model=SuccessResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Bildirishnomani o'qilgan deb belgilash
    """
    try:
        notif_uuid = uuid.UUID(notification_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noto'g'ri notification ID formati"
        )
    
    result = await db.execute(
        select(Notification).where(
            Notification.id == notif_uuid,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bildirishnoma topilmadi"
        )
    
    notification.read_at = datetime.utcnow()
    await db.commit()
    
    return SuccessResponse(message="Bildirishnoma o'qilgan deb belgilandi")


@router.post("/me/notifications/read-all", response_model=SuccessResponse)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Barcha bildirishnomalarni o'qilgan deb belgilash
    """
    from datetime import datetime
    
    await db.execute(
        update(Notification)
        .where(
            Notification.user_id == current_user.id,
            Notification.read_at.is_(None)
        )
        .values(read_at=datetime.utcnow())
    )
    await db.commit()
    
    return SuccessResponse(message="Barcha bildirishnomalar o'qilgan deb belgilandi")


@router.get("/me/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Foydalanuvchi statistikasi
    """
    # Get test sessions
    result = await db.execute(
        select(TestSession).where(TestSession.user_id == current_user.id)
    )
    test_sessions = result.scalars().all()
    
    # Get test results
    session_ids = [s.id for s in test_sessions]
    if session_ids:
        result = await db.execute(
            select(TestResult).where(TestResult.session_id.in_(session_ids))
        )
        test_results = result.scalars().all()
    else:
        test_results = []
    
    # Calculate stats
    total_sessions = len(test_sessions)
    completed_sessions = len([s for s in test_sessions if s.completed_at])
    total_tests = len(test_results)
    
    # Test type breakdown
    test_type_counts = {}
    for result in test_results:
        test_type = result.test_type.value
        test_type_counts[test_type] = test_type_counts.get(test_type, 0) + 1
    
    # Recent activity
    recent_sessions = sorted(test_sessions, key=lambda x: x.created_at, reverse=True)[:5]
    
    return {
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "total_tests": total_tests,
        "test_type_breakdown": test_type_counts,
        "recent_activity": [{
            "id": s.id,
            "started_at": s.created_at,
            "completed_at": s.completed_at,
            "status": s.status.value if s.status else None
        } for s in recent_sessions],
        "member_since": current_user.created_at
    }


@router.delete("/me", response_model=SuccessResponse)
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Foydalanuvchi hisobini o'chirish
    """
    # Soft delete - mark as inactive
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(is_active=False)
    )
    await db.commit()
    
    return SuccessResponse(message="Hisobingiz muvaffaqiyatli o'chirildi")
