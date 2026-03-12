"""
EyeCare Backend - Mobile API Routes

Mobile ilova uchun maxsus optimizatsiyalangan API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json
import secrets
import uuid as uuid_lib

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_token_pair, verify_password, hash_password
from app.api.deps import get_current_user, get_current_active_user
from app.models.user import User, Gender
from app.models.test import TestSession, TestResult, TestType
from app.models.doctor import Doctor, Appointment, AppointmentStatus
from app.models.notification import Notification
from app.schemas.common import SuccessResponse

router = APIRouter()


# ==================== MOBILE SCHEMAS ====================

class MobileRegisterRequest(BaseModel):
    """Mobile ro'yxatdan o'tish"""
    phone: str = Field(..., pattern=r"^\+?998[0-9]{9}$", example="+998901234567")
    password: str = Field(..., min_length=6, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    gender: Optional[str] = Field(None, pattern=r"^(male|female)$")
    birth_date: Optional[str] = Field(None, example="1990-01-15")
    device_id: Optional[str] = None
    fcm_token: Optional[str] = None


class MobileLoginRequest(BaseModel):
    """Mobile login"""
    phone: str = Field(..., pattern=r"^\+?998[0-9]{9}$")
    password: str = Field(..., min_length=6)
    device_id: Optional[str] = None
    fcm_token: Optional[str] = None


class MobileTokenResponse(BaseModel):
    """Mobile token javob"""
    success: bool = True
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class MobileTestStartRequest(BaseModel):
    """Test boshlash"""
    test_type: str = Field(..., example="snellen")
    device_info: Optional[str] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    device_ppi: Optional[float] = None


class MobileTestResultRequest(BaseModel):
    """Test natijasini yuborish"""
    session_id: str  # UUID as string
    test_type: str
    score: float = Field(..., ge=0, le=100)
    eye: str = Field(..., pattern=r"^(right|left|both)$")
    distance_cm: Optional[float] = None
    responses: Optional[List[dict]] = None
    duration_seconds: Optional[int] = None
    raw_data: Optional[dict] = None


class MobileDiagnosisRequest(BaseModel):
    """Tashxis so'rovi"""
    session_id: str  # UUID as string
    symptoms: Optional[List[str]] = None
    age: Optional[int] = None
    has_glasses: Optional[bool] = None
    family_history: Optional[List[str]] = None


# ==================== AUTH ENDPOINTS ====================

@router.post("/auth/register", response_model=MobileTokenResponse)
async def mobile_register(
    data: MobileRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Mobile ilovadan ro'yxatdan o'tish
    
    - Telefon raqam bilan ro'yxatdan o'tish
    - FCM token saqlash (push notification uchun)
    - Device ID saqlash (multi-device uchun)
    """
    # Check if phone exists
    result = await db.execute(
        select(User).where(User.phone == data.phone)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "PHONE_EXISTS", "message": "Bu telefon raqam ro'yxatdan o'tgan"}
        )
    
    # Parse birth_date
    birth_date = None
    if data.birth_date:
        try:
            birth_date = datetime.strptime(data.birth_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    # Create user
    user = User(
        phone=data.phone,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        gender=Gender(data.gender) if data.gender else None,
        birth_date=birth_date,
        fcm_token=data.fcm_token
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create tokens
    tokens = create_token_pair(user.id)
    
    return MobileTokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
        user={
            "id": user.id,
            "phone": user.phone,
            "full_name": user.full_name,
            "gender": user.gender.value if user.gender else None,
            "avatar_url": user.avatar_url
        }
    )


@router.post("/auth/login", response_model=MobileTokenResponse)
async def mobile_login(
    data: MobileLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Mobile ilovadan kirish
    
    - Telefon + parol bilan kirish
    - FCM token yangilash
    """
    result = await db.execute(
        select(User).where(User.phone == data.phone)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Telefon yoki parol noto'g'ri"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_DISABLED", "message": "Hisob o'chirilgan"}
        )
    
    # Update FCM token
    if data.fcm_token:
        user.fcm_token = data.fcm_token
        await db.commit()
    
    # Create tokens
    tokens = create_token_pair(user.id)
    
    return MobileTokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
        user={
            "id": user.id,
            "phone": user.phone,
            "full_name": user.full_name,
            "gender": user.gender.value if user.gender else None,
            "avatar_url": user.avatar_url
        }
    )


@router.post("/auth/refresh")
async def mobile_refresh_token(
    refresh_token: str = Header(..., alias="X-Refresh-Token"),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Token yangilash
    
    Header: X-Refresh-Token: <refresh_token>
    """
    from app.core.security import decode_token
    
    payload = decode_token(refresh_token)
    if not payload or payload.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Yaroqsiz refresh token"}
        )
    
    result = await db.execute(
        select(User).where(User.id == payload.sub)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_NOT_FOUND", "message": "Foydalanuvchi topilmadi"}
        )
    
    tokens = create_token_pair(user.id)
    
    return {
        "success": True,
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "expires_in": tokens.expires_in
    }


# ==================== USER ENDPOINTS ====================

@router.get("/user/profile")
async def get_mobile_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Foydalanuvchi profili
    """
    # Get test stats
    result = await db.execute(
        select(func.count(TestSession.id))
        .where(TestSession.user_id == current_user.id)
    )
    total_tests = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(TestSession.id))
        .where(
            TestSession.user_id == current_user.id,
            TestSession.completed_at.isnot(None)
        )
    )
    completed_tests = result.scalar() or 0
    
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "phone": current_user.phone,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "gender": current_user.gender.value if current_user.gender else None,
            "birth_date": current_user.birth_date.isoformat() if current_user.birth_date else None,
            "avatar_url": current_user.avatar_url,
            "created_at": current_user.created_at.isoformat()
        },
        "stats": {
            "total_tests": total_tests,
            "completed_tests": completed_tests
        }
    }


@router.put("/user/profile")
async def update_mobile_profile(
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    gender: Optional[str] = None,
    birth_date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Profil yangilash
    """
    if full_name:
        current_user.full_name = full_name
    if email:
        current_user.email = email
    if gender:
        current_user.gender = Gender(gender)
    if birth_date:
        try:
            current_user.birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    await db.commit()
    
    return {"success": True, "message": "Profil yangilandi"}


@router.put("/user/fcm-token")
async def update_fcm_token(
    fcm_token: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 FCM token yangilash (Push notification uchun)
    """
    current_user.fcm_token = fcm_token
    await db.commit()
    
    return {"success": True, "message": "FCM token yangilandi"}


# ==================== TEST ENDPOINTS ====================

@router.get("/tests/types")
async def get_test_types():
    """
    📱 Mavjud test turlari ro'yxati
    """
    tests = [
        {
            "type": "snellen",
            "name": "Ko'rish keskinligi",
            "name_en": "Visual Acuity",
            "description": "Snellen jadvali yordamida ko'rish o'tkirligini tekshirish",
            "distance_m": 5.0,
            "duration_min": 3,
            "icon": "eye",
            "category": "basic"
        },
        {
            "type": "ishihara",
            "name": "Rang ajratish",
            "name_en": "Color Blindness",
            "description": "Ishihara testlari orqali rang ko'rish qobiliyatini tekshirish",
            "distance_m": 0.75,
            "duration_min": 5,
            "icon": "palette",
            "category": "basic"
        },
        {
            "type": "astigmatism",
            "name": "Astigmatizm",
            "name_en": "Astigmatism",
            "description": "Ko'z astigmatizmini aniqlash",
            "distance_m": 0.5,
            "duration_min": 2,
            "icon": "radio-button-on",
            "category": "basic"
        },
        {
            "type": "amsler",
            "name": "Amsler panjarasi",
            "name_en": "Amsler Grid",
            "description": "Makulyar degeneratsiya va to'r parda muammolarini aniqlash",
            "distance_m": 0.3,
            "duration_min": 2,
            "icon": "grid",
            "category": "advanced"
        },
        {
            "type": "contrast",
            "name": "Kontrast sezgirlik",
            "name_en": "Contrast Sensitivity",
            "description": "Kontrast ko'rish qobiliyatini tekshirish",
            "distance_m": 1.0,
            "duration_min": 3,
            "icon": "contrast",
            "category": "advanced"
        },
        {
            "type": "near_vision",
            "name": "Yaqindan ko'rish",
            "name_en": "Near Vision",
            "description": "Yaqindan o'qish qobiliyatini tekshirish",
            "distance_m": 0.35,
            "duration_min": 2,
            "icon": "book",
            "category": "basic"
        },
        {
            "type": "duochrome",
            "name": "Duoxrom",
            "name_en": "Duochrome",
            "description": "Miopiya va gipermetropiyani aniqlash",
            "distance_m": 0.5,
            "duration_min": 2,
            "icon": "color-filter",
            "category": "advanced"
        },
        {
            "type": "peripheral",
            "name": "Periferik ko'rish",
            "name_en": "Peripheral Vision",
            "description": "Yon tomonlardan ko'rish qobiliyatini tekshirish",
            "distance_m": 0.5,
            "duration_min": 4,
            "icon": "scan",
            "category": "advanced"
        },
        {
            "type": "red_desaturation",
            "name": "Qizil desaturatsiya",
            "name_en": "Red Desaturation",
            "description": "Ko'rish asab funksiyasini tekshirish",
            "distance_m": 0.5,
            "duration_min": 2,
            "icon": "ellipse",
            "category": "specialized"
        },
        {
            "type": "dark_adaptation",
            "name": "Qorong'ulik adaptatsiyasi",
            "name_en": "Dark Adaptation",
            "description": "Qorong'uga moslashish qobiliyatini tekshirish",
            "distance_m": 0.4,
            "duration_min": 5,
            "icon": "moon",
            "category": "specialized"
        }
    ]
    
    return {
        "success": True,
        "tests": tests,
        "categories": {
            "basic": "Asosiy testlar",
            "advanced": "Kengaytirilgan testlar",
            "specialized": "Maxsus testlar"
        }
    }


@router.post("/tests/start")
async def start_mobile_test(
    data: MobileTestStartRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Yangi test sessiyasini boshlash
    """
    # Generate unique session token
    session_token = secrets.token_urlsafe(32)
    
    session = TestSession(
        user_id=current_user.id,
        session_token=session_token,
        source="mobile",
        device_type=data.device_info,
        screen_width=data.screen_width,
        screen_height=data.screen_height
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return {
        "success": True,
        "session_id": str(session.id),
        "session_token": session_token,
        "created_at": session.created_at.isoformat(),
        "test_type": data.test_type
    }


@router.post("/tests/submit")
async def submit_mobile_test_result(
    data: MobileTestResultRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Test natijasini yuborish
    """
    # Convert session_id string to UUID
    try:
        session_uuid = uuid_lib.UUID(data.session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_SESSION_ID", "message": "Noto'g'ri session ID formati"}
        )
    
    # Verify session belongs to user
    result = await db.execute(
        select(TestSession).where(
            TestSession.id == session_uuid,
            TestSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SESSION_NOT_FOUND", "message": "Test sessiyasi topilmadi"}
        )
    
    # Get current test count for order
    count_result = await db.execute(
        select(func.count(TestResult.id)).where(TestResult.session_id == session.id)
    )
    test_order = (count_result.scalar() or 0) + 1
    
    # Map eye string to EyeSide enum
    from app.models.test import EyeSide
    eye_map = {"right": EyeSide.RIGHT, "left": EyeSide.LEFT, "both": EyeSide.BOTH}
    eye_side = eye_map.get(data.eye, EyeSide.BOTH)
    
    # Create test result
    test_result = TestResult(
        session_id=session.id,
        test_type=TestType(data.test_type),
        test_order=test_order,
        score=str(data.score),
        eye_side=eye_side,
        distance_cm=int(data.distance_cm) if data.distance_cm else None,
        raw_data={
            "responses": data.responses,
            "duration_seconds": data.duration_seconds,
            "original_score": data.score,
            "extra_data": data.raw_data
        }
    )
    
    db.add(test_result)
    await db.commit()
    await db.refresh(test_result)
    
    # Determine status based on score
    if data.score >= 80:
        status_text = "normal"
        status_message = "Ko'rsatkichlar normal"
    elif data.score >= 50:
        status_text = "warning"
        status_message = "Ehtiyotkorlik talab etiladi"
    else:
        status_text = "concern"
        status_message = "Shifokorga murojaat tavsiya etiladi"
    
    return {
        "success": True,
        "result_id": test_result.id,
        "score": data.score,
        "status": status_text,
        "status_message": status_message,
        "created_at": test_result.created_at.isoformat()
    }


@router.post("/tests/complete")
async def complete_mobile_test(
    data: MobileDiagnosisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Test sessiyasini yakunlash va tashxis olish
    """
    from app.services.diagnosis_service import DiagnosisService
    
    # Get session with results
    try:
        session_uuid = uuid_lib.UUID(data.session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_SESSION_ID", "message": "Noto'g'ri session ID formati"}
        )
    
    result = await db.execute(
        select(TestSession)
        .options(selectinload(TestSession.results))
        .where(
            TestSession.id == session_uuid,
            TestSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SESSION_NOT_FOUND", "message": "Test sessiyasi topilmadi"}
        )
    
    # Analyze results
    analysis = DiagnosisService.analyze_results(
        test_results=session.results,
        symptoms=data.symptoms,
        age=data.age
    )
    
    # Update session with diagnosis info
    session.completed_at = datetime.utcnow()
    session.overall_status = analysis["risk_level"]
    session.concerns = analysis["detected_issues"]
    session.recommendations = analysis["recommendations"]
    
    await db.commit()
    
    return {
        "success": True,
        "session_id": str(session.id),
        "overall_score": analysis["overall_score"],
        "risk_level": analysis["risk_level"],
        "urgency": analysis["urgency"],
        "detected_issues": analysis["detected_issues"],
        "suspected_conditions": analysis["suspected_conditions"],
        "recommendations": analysis["recommendations"],
        "medicines": analysis["medicines"],
        "disclaimer": "Bu natijalar faqat dastlabki tekshiruvdir. Aniq tashxis uchun oftalmologga murojaat qiling."
    }


@router.get("/tests/history")
async def get_mobile_test_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Test tarixi
    """
    result = await db.execute(
        select(TestSession)
        .options(
            selectinload(TestSession.results)
        )
        .where(TestSession.user_id == current_user.id)
        .order_by(TestSession.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    sessions = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(TestSession.id))
        .where(TestSession.user_id == current_user.id)
    )
    total = count_result.scalar() or 0
    
    return {
        "success": True,
        "sessions": [{
            "id": str(s.id),
            "created_at": s.created_at.isoformat(),
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            "is_completed": s.completed_at is not None,
            "overall_status": s.overall_status,
            "results_count": len(s.results) if s.results else 0,
            "results": [{
                "test_type": r.test_type.value if r.test_type else None,
                "score": r.score,
                "eye": r.eye_side.value if r.eye_side else None
            } for r in (s.results or [])],
            "diagnosis": {
                "risk_level": s.overall_status,
                "concerns": s.concerns[:3] if s.concerns else [],
                "recommendations": s.recommendations[:3] if s.recommendations else []
            } if s.overall_status else None
        } for s in sessions],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.get("/tests/session/{session_id}")
async def get_mobile_test_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Bitta test sessiyasi batafsil
    """
    try:
        session_uuid = uuid_lib.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_SESSION_ID", "message": "Noto'g'ri session ID"}
        )
    
    result = await db.execute(
        select(TestSession)
        .options(
            selectinload(TestSession.results)
        )
        .where(
            TestSession.id == session_uuid,
            TestSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SESSION_NOT_FOUND", "message": "Sessiya topilmadi"}
        )
    
    return {
        "success": True,
        "session": {
            "id": str(session.id),
            "created_at": session.created_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "source": session.source,
            "overall_status": session.overall_status,
            "results": [{
                "id": str(r.id),
                "test_type": r.test_type.value,
                "score": r.score,
                "eye": r.eye_side.value if r.eye_side else None,
                "distance_cm": r.distance_cm,
                "created_at": r.created_at.isoformat(),
                "raw_data": r.raw_data
            } for r in session.results],
            "concerns": session.concerns,
            "recommendations": session.recommendations
        }
    }


# ==================== DOCTORS ENDPOINTS ====================

@router.get("/doctors")
async def get_mobile_doctors(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    specialization: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Shifokorlar ro'yxati
    """
    query = select(Doctor).where(Doctor.is_active == True)
    
    if specialization:
        query = query.where(Doctor.specialty.ilike(f"%{specialization}%"))
    
    query = query.order_by(Doctor.rating.desc())
    
    # Get total
    count_result = await db.execute(
        select(func.count(Doctor.id)).where(Doctor.is_active == True)
    )
    total = count_result.scalar() or 0
    
    # Paginate
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    doctors = result.scalars().all()
    
    return {
        "success": True,
        "doctors": [{
            "id": str(d.id),
            "full_name": d.full_name,
            "specialty": d.specialty,
            "experience": d.experience,
            "rating": d.rating,
            "avatar_url": d.avatar_url,
            "phone": d.phone,
            "address": d.address,
            "work_hours": d.work_hours
        } for d in doctors],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.get("/doctors/{doctor_id}")
async def get_mobile_doctor(
    doctor_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Shifokor haqida batafsil
    """
    try:
        doctor_uuid = uuid_lib.UUID(doctor_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_ID", "message": "Noto'g'ri doctor ID formati"}
        )
    
    result = await db.execute(
        select(Doctor).where(Doctor.id == doctor_uuid)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCTOR_NOT_FOUND", "message": "Shifokor topilmadi"}
        )
    
    return {
        "success": True,
        "doctor": {
            "id": str(doctor.id),
            "full_name": doctor.full_name,
            "specialty": doctor.specialty,
            "bio": doctor.bio,
            "experience": doctor.experience,
            "clinic_name": doctor.clinic_name,
            "rating": doctor.rating,
            "review_count": doctor.review_count,
            "avatar_url": doctor.avatar_url,
            "phone": doctor.phone,
            "email": doctor.email,
            "address": doctor.address,
            "work_hours": doctor.work_hours,
            "is_available": doctor.is_active
        }
    }


@router.post("/doctors/{doctor_id}/appointment")
async def book_mobile_appointment(
    doctor_id: str,
    appointment_date: str,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Shifokorga uchrashuv belgilash
    """
    # Parse doctor_id
    try:
        doctor_uuid = uuid_lib.UUID(doctor_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_ID", "message": "Noto'g'ri doctor ID formati"}
        )
    
    # Check doctor exists
    result = await db.execute(
        select(Doctor).where(Doctor.id == doctor_uuid, Doctor.is_active == True)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCTOR_NOT_FOUND", "message": "Shifokor topilmadi"}
        )
    
    # Parse date
    try:
        appointment_dt = datetime.fromisoformat(appointment_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_DATE", "message": "Noto'g'ri sana formati. ISO format ishlatilsin."}
        )
    
    # Create appointment
    appointment = Appointment(
        user_id=current_user.id,
        doctor_id=doctor_uuid,
        scheduled_at=appointment_dt,
        user_notes=notes,
        status=AppointmentStatus.PENDING
    )
    
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    
    return {
        "success": True,
        "appointment": {
            "id": str(appointment.id),
            "doctor_name": doctor.full_name,
            "scheduled_at": appointment.scheduled_at.isoformat(),
            "status": appointment.status.value,
            "created_at": appointment.created_at.isoformat()
        },
        "message": "Uchrashuv muvaffaqiyatli belgilandi"
    }


@router.get("/appointments")
async def get_mobile_appointments(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Mening uchrashuvlarim
    """
    query = (
        select(Appointment)
        .options(selectinload(Appointment.doctor))
        .where(Appointment.user_id == current_user.id)
    )
    
    if status_filter:
        query = query.where(Appointment.status == status_filter)
    
    query = query.order_by(Appointment.scheduled_at.desc())
    
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    return {
        "success": True,
        "appointments": [{
            "id": str(a.id),
            "doctor": {
                "id": str(a.doctor.id),
                "full_name": a.doctor.full_name,
                "specialty": a.doctor.specialty,
                "avatar_url": a.doctor.avatar_url
            } if a.doctor else None,
            "scheduled_at": a.scheduled_at.isoformat(),
            "status": a.status.value,
            "user_notes": a.user_notes,
            "created_at": a.created_at.isoformat()
        } for a in appointments]
    }


# ==================== NOTIFICATIONS ENDPOINTS ====================

@router.get("/notifications")
async def get_mobile_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Bildirishnomalar
    """
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.where(Notification.read_at.is_(None))
    
    query = query.order_by(Notification.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    # Get unread count
    unread_result = await db.execute(
        select(func.count(Notification.id))
        .where(
            Notification.user_id == current_user.id,
            Notification.read_at.is_(None)
        )
    )
    unread_count = unread_result.scalar() or 0
    
    return {
        "success": True,
        "notifications": [{
            "id": str(n.id),
            "title": n.title,
            "message": n.body,
            "type": n.type.value,
            "is_read": n.read_at is not None,
            "created_at": n.created_at.isoformat()
        } for n in notifications],
        "unread_count": unread_count
    }


@router.post("/notifications/{notification_id}/read")
async def mark_mobile_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Bildirishnomani o'qilgan deb belgilash
    """
    try:
        notif_uuid = uuid_lib.UUID(notification_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_ID", "message": "Noto'g'ri ID formati"}
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
            detail={"code": "NOT_FOUND", "message": "Bildirishnoma topilmadi"}
        )
    
    notification.read_at = datetime.utcnow()
    await db.commit()
    
    return {"success": True, "message": "Bildirishnoma o'qilgan deb belgilandi"}


@router.post("/notifications/read-all")
async def mark_all_mobile_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📱 Barcha bildirishnomalarni o'qilgan deb belgilash
    """
    await db.execute(
        update(Notification)
        .where(
            Notification.user_id == current_user.id,
            Notification.read_at.is_(None)
        )
        .values(read_at=datetime.utcnow())
    )
    await db.commit()
    
    return {"success": True, "message": "Barcha bildirishnomalar o'qildi"}


# ==================== UTILITY ENDPOINTS ====================

@router.get("/config")
async def get_mobile_config():
    """
    📱 Mobile ilova konfiguratsiyasi
    """
    return {
        "success": True,
        "config": {
            "app_name": settings.APP_NAME,
            "version": "1.0.0",
            "min_version": "1.0.0",
            "update_required": False,
            "maintenance_mode": False,
            "features": {
                "tests_enabled": True,
                "doctors_enabled": True,
                "appointments_enabled": True,
                "notifications_enabled": True
            },
            "contact": {
                "support_phone": "+998901234567",
                "support_email": "support@eyecare.uz",
                "telegram": "@eyecare_support"
            },
            "legal": {
                "privacy_policy_url": "https://eyecare.uz/privacy",
                "terms_url": "https://eyecare.uz/terms"
            }
        }
    }


@router.get("/diseases")
async def get_diseases_info():
    """
    📱 Ko'z kasalliklari haqida ma'lumot
    """
    from app.services.diagnosis_service import DiagnosisService
    
    diseases = []
    for key, info in DiagnosisService.DISEASES.items():
        diseases.append({
            "key": key,
            "name": info["name_uz"],
            "name_ru": info["name_ru"],
            "symptoms": info["symptoms"],
            "risk_factors": info["risk_factors"],
            "recommendations": info["recommendations"]
        })
    
    return {
        "success": True,
        "diseases": diseases
    }
