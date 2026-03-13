"""
EyeCare Backend - Schemas Module
All Pydantic schemas exported here.
"""

from app.schemas.user import (
    UserRegister, UserLogin, TelegramLogin, VerifyPhone,
    RefreshToken, PasswordReset, Token, TokenPayload,
    UserResponse, UserListResponse, UserUpdate, UserStats,
    ChangePassword, AdminLogin, AdminCreate, AdminResponse,
    AuthResponse
)
from app.schemas.test import (
    DeviceInfo, CalibrationData, TestSessionCreate,
    TestInfo, TestSessionResponse, TestSessionWithTests,
    SessionSummary, TestSessionComplete, TestResultCreate,
    TestResultResponse, TestResultWithName, ResultHistoryItem,
    ResultsHistoryResponse, DetailedResultResponse, UserStatistics,
    TestTrend, BotScreeningQuestion, BotScreeningResponse,
    BotTestResultCreate, BotTestDiagnosis
)
from app.schemas.doctor import (
    DoctorCreate, DoctorUpdate, DoctorResponse, DoctorListResponse,
    ReviewCreate, ReviewResponse, ReviewListResponse,
    AppointmentCreate, AppointmentUpdate, AppointmentResponse,
    AppointmentListResponse
)
from app.schemas.common import (
    PaginationParams, PaginatedResponse, SuccessResponse,
    ErrorResponse, ErrorDetail, HealthCheckResponse, HealthStatus,
    DateRangeFilter, LocationFilter, SortParams,
    CountStat, TrendStat, DashboardStats,
    NotificationResponse, NotificationListResponse,
    PublicSettings, SettingUpdate, FileUploadResponse
)

__all__ = [
    # User
    "UserRegister", "UserLogin", "TelegramLogin", "VerifyPhone",
    "RefreshToken", "PasswordReset", "Token", "TokenPayload",
    "UserResponse", "UserListResponse", "UserUpdate", "UserStats",
    "ChangePassword", "AdminLogin", "AdminCreate", "AdminResponse",
    "AuthResponse",
    
    # Test
    "DeviceInfo", "CalibrationData", "TestSessionCreate",
    "TestInfo", "TestSessionResponse", "TestSessionWithTests",
    "SessionSummary", "TestSessionComplete", "TestResultCreate",
    "TestResultResponse", "TestResultWithName", "ResultHistoryItem",
    "ResultsHistoryResponse", "DetailedResultResponse", "UserStatistics",
    "TestTrend", "BotScreeningQuestion", "BotScreeningResponse",
    "BotTestResultCreate", "BotTestDiagnosis",
    
    # Doctor
    "DoctorCreate", "DoctorUpdate", "DoctorResponse", "DoctorListResponse",
    "ReviewCreate", "ReviewResponse", "ReviewListResponse",
    "AppointmentCreate", "AppointmentUpdate", "AppointmentResponse",
    "AppointmentListResponse",
    
    # Common
    "PaginationParams", "PaginatedResponse", "SuccessResponse",
    "ErrorResponse", "ErrorDetail", "HealthCheckResponse", "HealthStatus",
    "DateRangeFilter", "LocationFilter", "SortParams",
    "CountStat", "TrendStat", "DashboardStats",
    "NotificationResponse", "NotificationListResponse",
    "PublicSettings", "SettingUpdate", "FileUploadResponse",
]
