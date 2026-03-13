"""
EyeCare Backend - API Package
"""

from fastapi import APIRouter

from app.api.routes import auth, tests, doctors, admin, users, mobile

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# User routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Test routes
api_router.include_router(tests.router, prefix="/tests", tags=["Tests"])

# Doctor routes
api_router.include_router(doctors.router, prefix="/doctors", tags=["Doctors"])

# Admin routes
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Mobile API routes
api_router.include_router(mobile.router, prefix="/mobile", tags=["Mobile API"])
