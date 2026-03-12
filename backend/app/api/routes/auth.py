"""
==============================================================================
EyeCare Backend - Authentication API
==============================================================================
User authentication endpoints: register, login, verify, refresh tokens.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from loguru import logger

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password, create_token_pair,
    verify_refresh_token, generate_verification_code
)
from app.core.redis import redis_manager
from app.models.user import User
from app.schemas.user import (
    UserRegister, UserLogin, VerifyPhone, RefreshToken,
    PasswordReset, AuthResponse, UserResponse, Token
)
from app.api.deps import get_current_user


router = APIRouter()


# ==============================================================================
# Helper Functions
# ==============================================================================

async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
    """Get user by phone number"""
    result = await db.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def send_verification_sms(phone: str, code: str) -> bool:
    """
    Send verification SMS via Eskiz.uz or other provider.
    TODO: Implement actual SMS sending
    """
    logger.info(f"📱 Sending verification code {code} to {phone}")
    # In development, just log the code
    return True


# ==============================================================================
# Registration
# ==============================================================================

@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user with phone number and password"
)
async def register(
    data: UserRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user:
    1. Check if phone already exists
    2. Create user with hashed password
    3. Generate and send verification code
    """
    # Check if phone already registered
    existing_user = await get_user_by_phone(db, data.phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu telefon raqami allaqachon ro'yxatdan o'tgan"
        )
    
    # Create new user
    user = User(
        phone=data.phone,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
        birth_date=data.birth_date,
        gender=data.gender,
        is_verified=False
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Generate verification code
    code = generate_verification_code()
    
    # Store code in Redis (5 minutes expiry)
    await redis_manager.set_verification_code(data.phone, code, expire_seconds=300)
    
    # Send SMS in background
    background_tasks.add_task(send_verification_sms, data.phone, code)
    
    logger.info(f"✅ New user registered: {user.id} ({data.phone})")
    
    return {
        "success": True,
        "message": "Tasdiqlash kodi yuborildi",
        "data": {
            "user_id": str(user.id),
            "phone": data.phone,
            "verification_required": True
        }
    }


# ==============================================================================
# Phone Verification
# ==============================================================================

@router.post(
    "/verify",
    response_model=AuthResponse,
    summary="Verify phone number",
    description="Verify phone number with SMS code"
)
async def verify_phone(
    data: VerifyPhone,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify phone number:
    1. Check verification code
    2. Mark user as verified
    3. Return tokens
    """
    # Get stored code
    stored_code = await redis_manager.get_verification_code(data.phone)
    
    if not stored_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tasdiqlash kodi muddati tugagan"
        )
    
    if stored_code != data.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noto'g'ri tasdiqlash kodi"
        )
    
    # Get user
    user = await get_user_by_phone(db, data.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )
    
    # Mark as verified
    user.is_verified = True
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = request.client.host if request.client else None
    user.login_count += 1
    
    await db.commit()
    await db.refresh(user)
    
    # Delete verification code
    await redis_manager.delete_verification_code(data.phone)
    
    # Create tokens
    tokens = create_token_pair(str(user.id))
    
    logger.info(f"✅ User verified: {user.id}")
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in
    )


# ==============================================================================
# Login
# ==============================================================================

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login with phone and password",
    description="Authenticate user with phone number and password"
)
async def login(
    data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    User login:
    1. Find user by phone
    2. Verify password
    3. Check if verified and not blocked
    4. Return tokens
    """
    # Get user
    user = await get_user_by_phone(db, data.phone)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri telefon raqami yoki parol"
        )
    
    # Verify password
    if not verify_password(data.password, user.password_hash):
        # Increment failed attempts
        user.failed_login_attempts += 1
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri telefon raqami yoki parol"
        )
    
    # Check if blocked
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Hisobingiz bloklangan: {user.blocked_reason or 'Sabab ko`rsatilmagan'}"
        )
    
    # Check if verified (allow login but flag it)
    if not user.is_verified:
        # Generate new code and send
        code = generate_verification_code()
        await redis_manager.set_verification_code(data.phone, code, expire_seconds=300)
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Telefon raqamingiz tasdiqlanmagan. Yangi kod yuborildi."
        )
    
    # Update login stats
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = request.client.host if request.client else None
    user.login_count += 1
    user.failed_login_attempts = 0
    
    await db.commit()
    await db.refresh(user)
    
    # Create tokens
    tokens = create_token_pair(str(user.id))
    
    logger.info(f"✅ User logged in: {user.id}")
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in
    )


# ==============================================================================
# Token Refresh
# ==============================================================================

@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    data: RefreshToken,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token:
    1. Verify refresh token
    2. Get user
    3. Create new token pair
    """
    # Verify refresh token
    user_id = verify_refresh_token(data.refresh_token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri yoki muddati o'tgan token"
        )
    
    # Get user
    user = await get_user_by_id(db, user_id)
    
    if not user or not user.is_active or user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Foydalanuvchi topilmadi yoki bloklangan"
        )
    
    # Create new tokens
    tokens = create_token_pair(str(user.id))
    
    return Token(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in
    )


# ==============================================================================
# Logout
# ==============================================================================

@router.post(
    "/logout",
    response_model=dict,
    summary="Logout user",
    description="Invalidate user session"
)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user:
    - In a production app, you would blacklist the token
    - For now, just return success
    """
    logger.info(f"👋 User logged out: {current_user.id}")
    
    return {
        "success": True,
        "message": "Muvaffaqiyatli chiqildi"
    }


# ==============================================================================
# Password Reset
# ==============================================================================

@router.post(
    "/forgot-password",
    response_model=dict,
    summary="Request password reset",
    description="Send password reset code to phone"
)
async def forgot_password(
    phone: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset:
    1. Find user by phone
    2. Generate reset code
    3. Send SMS
    """
    user = await get_user_by_phone(db, phone)
    
    # Don't reveal if user exists
    if user:
        code = generate_verification_code()
        await redis_manager.set_verification_code(f"reset:{phone}", code, expire_seconds=300)
        background_tasks.add_task(send_verification_sms, phone, code)
    
    return {
        "success": True,
        "message": "Agar bu raqam ro'yxatdan o'tgan bo'lsa, kod yuborildi"
    }


@router.post(
    "/reset-password",
    response_model=dict,
    summary="Reset password",
    description="Reset password with verification code"
)
async def reset_password(
    data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password:
    1. Verify reset code
    2. Update password
    """
    # Get stored code
    stored_code = await redis_manager.get_verification_code(f"reset:{data.phone}")
    
    if not stored_code or stored_code != data.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noto'g'ri yoki muddati o'tgan kod"
        )
    
    # Get user
    user = await get_user_by_phone(db, data.phone)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )
    
    # Update password
    user.password_hash = hash_password(data.new_password)
    user.failed_login_attempts = 0
    
    await db.commit()
    
    # Delete reset code
    await redis_manager.delete_verification_code(f"reset:{data.phone}")
    
    logger.info(f"🔐 Password reset for user: {user.id}")
    
    return {
        "success": True,
        "message": "Parol muvaffaqiyatli yangilandi"
    }


# ==============================================================================
# Resend Verification Code
# ==============================================================================

@router.post(
    "/resend-code",
    response_model=dict,
    summary="Resend verification code",
    description="Resend SMS verification code"
)
async def resend_code(
    phone: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Resend verification code with rate limiting
    """
    # Check rate limit (max 3 per 15 minutes)
    is_allowed, remaining = await redis_manager.rate_limit_check(
        f"resend:{phone}",
        max_requests=3,
        window_seconds=900
    )
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Juda ko'p so'rov. 15 daqiqadan so'ng qayta urinib ko'ring."
        )
    
    user = await get_user_by_phone(db, phone)
    
    if user and not user.is_verified:
        code = generate_verification_code()
        await redis_manager.set_verification_code(phone, code, expire_seconds=300)
        background_tasks.add_task(send_verification_sms, phone, code)
    
    return {
        "success": True,
        "message": "Tasdiqlash kodi yuborildi",
        "remaining_attempts": remaining
    }
