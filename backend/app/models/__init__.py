"""
EyeCare Backend - Models Module
All SQLAlchemy models exported here.
"""

from app.core.database import Base
from app.models.user import User, Admin, Gender, UserRole
from app.models.test import (
    TestSession, TestResult, BotTestSession,
    TestStatus, ResultStatus, TestType, EyeSide
)
from app.models.doctor import Doctor, DoctorReview, Appointment, AppointmentStatus
from app.models.telegram import TelegramSession, BotMessage
from app.models.notification import (
    Notification, AppSettings, ActivityLog,
    NotificationType, NotificationChannel, NotificationStatus
)

__all__ = [
    # Base
    "Base",
    
    # User
    "User",
    "Admin",
    "Gender",
    "UserRole",
    
    # Test
    "TestSession",
    "TestResult",
    "BotTestSession",
    "TestStatus",
    "ResultStatus",
    "TestType",
    "EyeSide",
    
    # Doctor
    "Doctor",
    "DoctorReview",
    "Appointment",
    "AppointmentStatus",
    
    # Telegram
    "TelegramSession",
    "BotMessage",
    
    # Notification
    "Notification",
    "AppSettings",
    "ActivityLog",
    "NotificationType",
    "NotificationChannel",
    "NotificationStatus",
]
