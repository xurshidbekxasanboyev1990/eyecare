"""
==============================================================================
EyeCare Backend - API Dependencies
==============================================================================
Shared dependencies for API routes: authentication, pagination, etc.
"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Header, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.core.security import verify_access_token
from app.core.redis import redis_manager
from app.models.user import User, Admin, UserRole
from app.schemas.common import PaginationParams


# ==============================================================================
# Security Scheme
# ==============================================================================

security = HTTPBearer(auto_error=False)


# ==============================================================================
# User Authentication
# ==============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Raises:
        HTTPException 401: If token is invalid or user not found
        HTTPException 403: If user is blocked
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentifikatsiya talab qilinadi",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify token
    user_id = verify_access_token(credentials.credentials)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri yoki muddati o'tgan token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Foydalanuvchi topilmadi"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hisob faol emas"
        )
    
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Hisobingiz bloklangan: {user.blocked_reason or 'Sabab ko`rsatilmagan'}"
        )
    
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    Used for endpoints that support both authenticated and anonymous access.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


# Alias for compatibility
get_current_active_user = get_current_user


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Admin:
    """
    Get current authenticated admin.
    
    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If not admin
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin autentifikatsiyasi talab qilinadi",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify token
    admin_id = verify_access_token(credentials.credentials)
    
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri yoki muddati o'tgan token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get admin from database
    result = await db.execute(
        select(Admin).where(Admin.id == admin_id)
    )
    admin = result.scalar_one_or_none()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin huquqlari talab qilinadi"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin hisobi faol emas"
        )
    
    return admin


def require_role(allowed_roles: list[UserRole]):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role([UserRole.ADMIN]))):
            ...
    """
    async def check_role(
        user: User = Depends(get_current_user)
    ) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu amalni bajarish uchun ruxsatingiz yo'q"
            )
        return user
    
    return check_role


# ==============================================================================
# Pagination
# ==============================================================================

def get_pagination(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page")
) -> PaginationParams:
    """Get pagination parameters"""
    return PaginationParams(page=page, limit=limit)


# ==============================================================================
# Rate Limiting
# ==============================================================================

async def check_rate_limit(
    request_key: str,
    max_requests: int = 60,
    window_seconds: int = 60
) -> bool:
    """
    Check rate limit for a given key.
    
    Args:
        request_key: Unique key for rate limiting (e.g., user_id, IP)
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
        
    Returns:
        True if allowed, raises HTTPException if rate limited
    """
    is_allowed, remaining = await redis_manager.rate_limit_check(
        f"rate:{request_key}",
        max_requests=max_requests,
        window_seconds=window_seconds
    )
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="So'rovlar limiti oshdi. Biroz kutib qayta urinib ko'ring.",
            headers={
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": str(window_seconds)
            }
        )
    
    return True


# ==============================================================================
# Session Token Validation
# ==============================================================================

async def validate_session_token(
    session_token: str = Header(..., alias="X-Session-Token"),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate test session token.
    Used for anonymous test sessions.
    """
    from app.models.test import TestSession
    
    result = await db.execute(
        select(TestSession).where(TestSession.session_token == session_token)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test sessiyasi topilmadi"
        )
    
    return session


# ==============================================================================
# Language Header
# ==============================================================================

def get_language(
    accept_language: str = Header(default="uz", alias="Accept-Language")
) -> str:
    """Get preferred language from header"""
    # Parse Accept-Language header
    supported = ["uz", "ru", "en"]
    
    for lang in accept_language.split(","):
        lang_code = lang.split(";")[0].strip()[:2].lower()
        if lang_code in supported:
            return lang_code
    
    return "uz"


# ==============================================================================
# Type Aliases
# ==============================================================================

CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[Optional[User], Depends(get_current_user_optional)]
CurrentAdmin = Annotated[Admin, Depends(get_current_admin)]
Pagination = Annotated[PaginationParams, Depends(get_pagination)]
Language = Annotated[str, Depends(get_language)]
