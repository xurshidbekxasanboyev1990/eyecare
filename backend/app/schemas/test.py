"""
==============================================================================
EyeCare Backend - Test Schemas
==============================================================================
Pydantic schemas for test-related API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID

from app.models.test import TestStatus, ResultStatus, TestType, EyeSide


# ==============================================================================
# Test Session Schemas
# ==============================================================================

class DeviceInfo(BaseModel):
    """Device information for test session"""
    type: Optional[str] = Field(None, description="Device type: mobile, tablet, desktop")
    browser: Optional[str] = None
    os: Optional[str] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None


class CalibrationData(BaseModel):
    """Distance calibration data"""
    distance_cm: Optional[int] = Field(None, ge=10, le=500)
    ipd_mm: Optional[float] = Field(None, ge=40, le=80, description="Inter-pupillary distance")


class TestSessionCreate(BaseModel):
    """Create test session request"""
    device_info: Optional[DeviceInfo] = None
    calibration: Optional[CalibrationData] = None
    source: str = Field(default="web", pattern="^(web|mobile|bot)$")


class TestInfo(BaseModel):
    """Test information for session"""
    type: str
    name: str
    order: int
    required_distance_cm: int
    estimated_duration_seconds: int


class TestSessionResponse(BaseModel):
    """Test session response"""
    id: UUID
    session_token: str
    user_id: Optional[UUID] = None
    source: str
    status: TestStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    overall_status: Optional[str] = None
    pdf_url: Optional[str] = None
    tests_completed: int = 0
    
    model_config = {"from_attributes": True}


class TestSessionWithTests(TestSessionResponse):
    """Test session with available tests"""
    tests: List[TestInfo]
    expires_at: datetime


class SessionSummary(BaseModel):
    """Test session summary"""
    overall_status: str
    tests_completed: int
    concerns: List[str] = []
    recommendations: List[str] = []


class TestSessionComplete(BaseModel):
    """Complete test session response"""
    session_id: UUID
    summary: SessionSummary
    pdf_url: Optional[str] = None


# ==============================================================================
# Test Result Schemas
# ==============================================================================

class TestResultCreate(BaseModel):
    """Create test result request"""
    test_type: TestType
    test_order: int = Field(..., ge=1, le=20)
    eye_side: EyeSide = EyeSide.BOTH
    score: Optional[str] = None
    status: ResultStatus = ResultStatus.NORMAL
    details: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    distance_cm: Optional[int] = Field(None, ge=10, le=500)


class TestResultResponse(BaseModel):
    """Test result response"""
    id: UUID
    session_id: UUID
    test_type: TestType
    test_order: int
    eye_side: EyeSide
    score: Optional[str] = None
    status: ResultStatus
    details: Optional[str] = None
    duration_seconds: Optional[int] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class TestResultWithName(TestResultResponse):
    """Test result with test name"""
    test_name: str


# ==============================================================================
# Results History Schemas
# ==============================================================================

class ResultHistoryItem(BaseModel):
    """Single result history item"""
    session_id: UUID
    completed_at: datetime
    overall_status: str
    tests_count: int
    duration_seconds: Optional[int]
    pdf_url: Optional[str]


class ResultsHistoryResponse(BaseModel):
    """Results history response"""
    items: List[ResultHistoryItem]
    total: int
    page: int
    limit: int


class DetailedResultResponse(BaseModel):
    """Detailed result response"""
    session: TestSessionResponse
    results: List[TestResultWithName]
    summary: SessionSummary
    pdf_url: Optional[str]


# ==============================================================================
# Statistics Schemas
# ==============================================================================

class TestTrend(BaseModel):
    """Test trend data"""
    test_type: str
    trend: str  # "improving", "stable", "declining"
    history: List[Dict[str, Any]]


class UserStatistics(BaseModel):
    """User test statistics"""
    total_sessions: int
    first_test_date: Optional[datetime]
    last_test_date: Optional[datetime]
    average_duration_seconds: int
    test_frequency: Dict[str, float]  # monthly, average_days_between
    trends: List[TestTrend]
    next_recommended_test: Optional[datetime]


# ==============================================================================
# Bot Test Schemas
# ==============================================================================

class BotScreeningQuestion(BaseModel):
    """Bot screening question"""
    question_id: str
    answer: str  # "yes", "no", "sometimes", "often"


class BotScreeningResponse(BaseModel):
    """Bot screening response"""
    next_question: Optional[str] = None
    recommended_test: Optional[str] = None
    web_app_url: Optional[str] = None
    is_complete: bool = False


class BotTestResultCreate(BaseModel):
    """Bot test result creation"""
    telegram_id: int
    test_type: str
    score: Optional[str] = None
    status: str
    details: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class BotTestDiagnosis(BaseModel):
    """Bot test diagnosis result"""
    condition: str
    condition_name_uz: str
    severity: str  # "mild", "moderate", "severe"
    medications: List[Dict[str, str]]
    recommendations: List[str]
    disclaimer: str
