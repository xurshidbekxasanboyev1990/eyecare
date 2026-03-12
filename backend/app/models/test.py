"""
==============================================================================
EyeCare Backend - Test Models
==============================================================================
Test session and result models for eye examination tracking.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, Integer, DateTime, Text, Float,
    ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.core.database import Base


class TestStatus(str, enum.Enum):
    """Test session status"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    EXPIRED = "expired"


class ResultStatus(str, enum.Enum):
    """Individual test result status"""
    NORMAL = "normal"
    WARNING = "warning"
    CONCERN = "concern"
    SKIPPED = "skipped"


class TestType(str, enum.Enum):
    """Available test types"""
    # Web App Tests
    VISUAL_ACUITY = "visual_acuity"
    COLOR_BLINDNESS = "color_blindness"
    AMSLER_GRID = "amsler_grid"
    CONTRAST = "contrast"
    ASTIGMATISM = "astigmatism"
    DUOCHROME = "duochrome"
    NEAR_VISION = "near_vision"
    RED_DESATURATION = "red_desaturation"
    PERIMETRY = "perimetry"
    DRY_EYE = "dry_eye"
    
    # Bot-specific Tests
    GLAUCOMA = "glaucoma"
    CATARACT = "cataract"
    MYOPIA = "myopia"
    CHORIORETINITIS = "chorioretinitis"
    RETINAL_DYSTROPHY = "retinal_dystrophy"


class EyeSide(str, enum.Enum):
    """Eye being tested"""
    RIGHT = "right"
    LEFT = "left"
    BOTH = "both"


class TestSession(Base):
    """
    Test session model - represents a complete testing session.
    Links to individual test results and user.
    """
    __tablename__ = "test_sessions"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Foreign Keys ====
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # ==== Session Token ====
    session_token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )
    
    # ==== Source ====
    source: Mapped[str] = mapped_column(
        String(20),
        default="web"  # "web", "mobile", "bot"
    )
    
    # ==== Timing ====
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # ==== Device Info ====
    device_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    screen_width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    screen_height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ==== Calibration ====
    calibrated_distance_cm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ipd_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # ==== Status ====
    status: Mapped[TestStatus] = mapped_column(
        SQLEnum(TestStatus),
        default=TestStatus.IN_PROGRESS
    )
    
    # ==== PDF ====
    pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # ==== Summary ====
    overall_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    concerns: Mapped[Optional[List]] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[Optional[List]] = mapped_column(JSONB, nullable=True)
    
    # ==== Timestamps ====
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # ==== Relationships ====
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="test_sessions"
    )
    results: Mapped[List["TestResult"]] = relationship(
        "TestResult",
        back_populates="session",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    # ==== Indexes ====
    __table_args__ = (
        Index("idx_test_sessions_status", "status"),
        Index("idx_test_sessions_created_at", "created_at"),
        Index("idx_test_sessions_source", "source"),
    )
    
    def __repr__(self) -> str:
        return f"<TestSession {self.id}: {self.status.value}>"
    
    @property
    def tests_completed(self) -> int:
        """Count completed tests"""
        return len([r for r in self.results if r.status != ResultStatus.SKIPPED])


class TestResult(Base):
    """
    Individual test result within a session.
    Stores score, status, and detailed data for each test type.
    """
    __tablename__ = "test_results"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Foreign Key ====
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("test_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # ==== Test Info ====
    test_type: Mapped[TestType] = mapped_column(
        SQLEnum(TestType),
        nullable=False
    )
    test_order: Mapped[int] = mapped_column(Integer, nullable=False)
    eye_side: Mapped[EyeSide] = mapped_column(
        SQLEnum(EyeSide),
        default=EyeSide.BOTH
    )
    
    # ==== Results ====
    score: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[ResultStatus] = mapped_column(
        SQLEnum(ResultStatus),
        default=ResultStatus.NORMAL
    )
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # ==== Timing ====
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # ==== Distance ====
    distance_cm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # ==== Timestamps ====
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # ==== Relationships ====
    session: Mapped["TestSession"] = relationship(
        "TestSession",
        back_populates="results"
    )
    
    # ==== Indexes ====
    __table_args__ = (
        Index("idx_test_results_test_type", "test_type"),
        Index("idx_test_results_status", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<TestResult {self.test_type.value}: {self.status.value}>"


class BotTestSession(Base):
    """
    Bot-specific test session for Telegram bot screening.
    Follows the specific screening flow (Katarakta, Miopiya, Glaukoma, etc.)
    """
    __tablename__ = "bot_test_sessions"
    
    # ==== Primary Key ====
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # ==== Telegram Info ====
    telegram_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )
    
    # ==== User Info (collected during screening) ====
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # ==== Screening Questions ====
    has_eye_fatigue: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # no/sometimes/often
    has_foggy_vision: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    has_burning: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    has_distant_blur: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    has_peripheral_darkness: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    has_floaters: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # ==== Detected Conditions ====
    suspected_conditions: Mapped[Optional[List]] = mapped_column(JSONB, nullable=True)
    
    # ==== Test Results ====
    test_results: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # ==== Recommendation ====
    recommended_tests: Mapped[Optional[List]] = mapped_column(JSONB, nullable=True)
    medications: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # ==== Status ====
    current_step: Mapped[str] = mapped_column(String(50), default="start")
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # ==== Timestamps ====
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # ==== Indexes ====
    __table_args__ = (
        Index("idx_bot_sessions_telegram_id", "telegram_id"),
        Index("idx_bot_sessions_completed", "is_completed"),
    )
    
    def __repr__(self) -> str:
        return f"<BotTestSession {self.id}: {self.current_step}>"
