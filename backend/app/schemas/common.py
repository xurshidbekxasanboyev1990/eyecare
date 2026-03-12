"""
==============================================================================
EyeCare Backend - Common Schemas
==============================================================================
Shared schemas used across multiple endpoints.
"""

from datetime import datetime
from typing import Optional, List, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from uuid import UUID


# ==============================================================================
# Generic Types
# ==============================================================================

T = TypeVar("T")


# ==============================================================================
# Pagination
# ==============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, limit: int):
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )


# ==============================================================================
# API Response Wrappers
# ==============================================================================

class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorDetail(BaseModel):
    """Error detail for validation errors"""
    field: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: dict = Field(
        default_factory=lambda: {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred"
        }
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==============================================================================
# Health Check
# ==============================================================================

class HealthStatus(BaseModel):
    """Health check component status"""
    status: str  # "healthy", "unhealthy", "degraded"
    latency_ms: Optional[float] = None
    message: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    uptime_seconds: float
    timestamp: datetime
    components: dict[str, HealthStatus]


# ==============================================================================
# Filters
# ==============================================================================

class DateRangeFilter(BaseModel):
    """Date range filter"""
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class LocationFilter(BaseModel):
    """Location-based filter"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=10, ge=1, le=100)


# ==============================================================================
# Sorting
# ==============================================================================

class SortParams(BaseModel):
    """Sorting parameters"""
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


# ==============================================================================
# Statistics
# ==============================================================================

class CountStat(BaseModel):
    """Simple count statistic"""
    total: int
    today: int
    this_week: int
    this_month: int


class TrendStat(BaseModel):
    """Trend statistic with comparison"""
    current: int
    previous: int
    change_percent: float
    trend: str  # "up", "down", "stable"


class DashboardStats(BaseModel):
    """Admin dashboard statistics"""
    users: CountStat
    tests: CountStat
    appointments: CountStat
    doctors: dict[str, int]


# ==============================================================================
# Notification Schemas
# ==============================================================================

class NotificationResponse(BaseModel):
    """Notification response"""
    id: UUID
    type: str
    title: str
    body: str
    data: Optional[dict]
    channel: str
    status: str
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Notification list response"""
    items: List[NotificationResponse]
    total: int
    unread_count: int


# ==============================================================================
# Settings Schemas
# ==============================================================================

class PublicSettings(BaseModel):
    """Public application settings"""
    app_name: str
    app_version: str
    maintenance_mode: bool
    supported_languages: List[str]
    test_distances: dict[str, int]
    enabled_tests: List[str]


class SettingUpdate(BaseModel):
    """Setting update request"""
    value: Any
    description: Optional[str] = None


# ==============================================================================
# File Upload
# ==============================================================================

class FileUploadResponse(BaseModel):
    """File upload response"""
    filename: str
    url: str
    size: int
    content_type: str
    uploaded_at: datetime
