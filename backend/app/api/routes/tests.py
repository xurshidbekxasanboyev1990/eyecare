"""
==============================================================================
EyeCare Backend - Test API Routes
==============================================================================
Test session and results management endpoints.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from loguru import logger

from app.core.database import get_db
from app.core.security import generate_session_token
from app.core.config import TEST_DISTANCES, TEST_NAMES_UZ
from app.models.test import TestSession, TestResult, TestStatus, ResultStatus, TestType
from app.models.user import User
from app.schemas.test import (
    TestSessionCreate, TestSessionResponse, TestSessionWithTests,
    TestResultCreate, TestResultResponse, TestResultWithName,
    TestInfo, SessionSummary, TestSessionComplete,
    ResultHistoryItem, ResultsHistoryResponse, DetailedResultResponse
)
from app.schemas.common import PaginationParams
from app.api.deps import get_current_user_optional, get_pagination, CurrentUser, OptionalUser


router = APIRouter()


# ==============================================================================
# Helper Functions
# ==============================================================================

def get_available_tests() -> List[TestInfo]:
    """Get list of available tests with info"""
    tests = [
        ("visual_acuity", 1, 120),
        ("color_blindness", 2, 90),
        ("amsler_grid", 3, 60),
        ("contrast", 4, 90),
        ("astigmatism", 5, 60),
        ("duochrome", 6, 60),
        ("near_vision", 7, 90),
        ("red_desaturation", 8, 60),
        ("perimetry", 9, 120),
        ("dry_eye", 10, 60),
    ]
    
    return [
        TestInfo(
            type=test_type,
            name=TEST_NAMES_UZ.get(test_type, test_type),
            order=order,
            required_distance_cm=TEST_DISTANCES.get(test_type, 50),
            estimated_duration_seconds=duration
        )
        for test_type, order, duration in tests
    ]


def calculate_overall_status(results: List[TestResult]) -> str:
    """Calculate overall session status from results"""
    if not results:
        return "unknown"
    
    concern_count = sum(1 for r in results if r.status == ResultStatus.CONCERN)
    warning_count = sum(1 for r in results if r.status == ResultStatus.WARNING)
    
    if concern_count > 0:
        return "concern"
    elif warning_count > 0:
        return "warning"
    return "normal"


def generate_recommendations(results: List[TestResult]) -> List[str]:
    """Generate recommendations based on test results"""
    recommendations = []
    
    for result in results:
        if result.status == ResultStatus.CONCERN:
            if result.test_type == TestType.VISUAL_ACUITY:
                recommendations.append("Ko'rish o'tkirligingiz pasaygan. Oftalmologga murojaat qiling.")
            elif result.test_type == TestType.COLOR_BLINDNESS:
                recommendations.append("Rang ko'rish buzilishi aniqlandi. Mutaxassis tekshiruvidan o'ting.")
            elif result.test_type == TestType.AMSLER_GRID:
                recommendations.append("To'r parda muammosi bo'lishi mumkin. Zudlik bilan shifokorga murojaat qiling.")
            elif result.test_type == TestType.CONTRAST:
                recommendations.append("Kontrast sezgirligi pasaygan. Bu katarakta belgisi bo'lishi mumkin.")
            elif result.test_type == TestType.PERIMETRY:
                recommendations.append("Periferik ko'rish muammosi aniqlandi. Glaukoma tekshiruvidan o'ting.")
    
    if not recommendations:
        recommendations.append("Testlar normal natija ko'rsatdi. 6 oydan so'ng qayta tekshiruvdan o'ting.")
    
    return recommendations


# ==============================================================================
# Session Management
# ==============================================================================

@router.post(
    "/sessions",
    response_model=TestSessionWithTests,
    status_code=status.HTTP_201_CREATED,
    summary="Start new test session",
    description="Create a new test session. Can be anonymous or authenticated."
)
async def create_session(
    data: TestSessionCreate,
    request: Request,
    user: OptionalUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new test session:
    1. Generate session token
    2. Store device info and calibration
    3. Return available tests
    """
    session = TestSession(
        user_id=user.id if user else None,
        session_token=generate_session_token(),
        source=data.source,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )
    
    # Add device info
    if data.device_info:
        session.device_type = data.device_info.type
        session.browser = data.device_info.browser
        session.os = data.device_info.os
        session.screen_width = data.device_info.screen_width
        session.screen_height = data.device_info.screen_height
    
    # Add calibration data
    if data.calibration:
        session.calibrated_distance_cm = data.calibration.distance_cm
        session.ipd_mm = data.calibration.ipd_mm
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    logger.info(f"📋 New test session created: {session.id}")
    
    return TestSessionWithTests(
        id=session.id,
        session_token=session.session_token,
        user_id=session.user_id,
        source=session.source,
        status=session.status,
        started_at=session.started_at,
        tests_completed=0,
        tests=get_available_tests(),
        expires_at=datetime.utcnow() + timedelta(hours=2)
    )


@router.get(
    "/sessions/{session_id}",
    response_model=TestSessionResponse,
    summary="Get test session",
    description="Get test session details by ID"
)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get test session by ID"""
    result = await db.execute(
        select(TestSession).where(TestSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test sessiyasi topilmadi"
        )
    
    return TestSessionResponse.model_validate(session)


# ==============================================================================
# Test Results
# ==============================================================================

@router.post(
    "/sessions/{session_id}/results",
    response_model=TestResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save test result",
    description="Save individual test result within a session"
)
async def save_result(
    session_id: UUID,
    data: TestResultCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Save test result:
    1. Verify session exists and is active
    2. Create result record
    3. Return saved result
    """
    # Get session
    result = await db.execute(
        select(TestSession).where(TestSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test sessiyasi topilmadi"
        )
    
    if session.status != TestStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu sessiya allaqachon yakunlangan"
        )
    
    # Create result
    test_result = TestResult(
        session_id=session_id,
        test_type=data.test_type,
        test_order=data.test_order,
        eye_side=data.eye_side,
        score=data.score,
        status=data.status,
        details=data.details,
        raw_data=data.raw_data,
        duration_seconds=data.duration_seconds,
        distance_cm=data.distance_cm,
        started_at=datetime.utcnow() - timedelta(seconds=data.duration_seconds or 0),
        completed_at=datetime.utcnow()
    )
    
    db.add(test_result)
    await db.commit()
    await db.refresh(test_result)
    
    logger.info(f"📝 Test result saved: {test_result.test_type.value} = {test_result.status.value}")
    
    return TestResultResponse.model_validate(test_result)


@router.post(
    "/sessions/{session_id}/complete",
    response_model=TestSessionComplete,
    summary="Complete test session",
    description="Mark session as complete and generate summary"
)
async def complete_session(
    session_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete test session:
    1. Calculate overall status
    2. Generate recommendations
    3. Trigger PDF generation
    """
    # Get session with results
    result = await db.execute(
        select(TestSession).where(TestSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test sessiyasi topilmadi"
        )
    
    if session.status == TestStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu sessiya allaqachon yakunlangan"
        )
    
    # Get results
    results_query = await db.execute(
        select(TestResult).where(TestResult.session_id == session_id)
    )
    results = results_query.scalars().all()
    
    # Calculate summary
    overall_status = calculate_overall_status(results)
    concerns = [r.test_type.value for r in results if r.status == ResultStatus.CONCERN]
    recommendations = generate_recommendations(results)
    
    # Update session
    session.status = TestStatus.COMPLETED
    session.completed_at = datetime.utcnow()
    session.duration_seconds = int((session.completed_at - session.started_at).total_seconds())
    session.overall_status = overall_status
    session.concerns = concerns
    session.recommendations = recommendations
    
    await db.commit()
    await db.refresh(session)
    
    # TODO: Trigger PDF generation in background
    # background_tasks.add_task(generate_pdf, session_id)
    
    logger.info(f"✅ Test session completed: {session_id} - {overall_status}")
    
    return TestSessionComplete(
        session_id=session.id,
        summary=SessionSummary(
            overall_status=overall_status,
            tests_completed=len(results),
            concerns=concerns,
            recommendations=recommendations
        ),
        pdf_url=session.pdf_url
    )


# ==============================================================================
# Results History
# ==============================================================================

@router.get(
    "/results",
    response_model=ResultsHistoryResponse,
    summary="Get test history",
    description="Get user's test history with pagination"
)
async def get_results_history(
    user: CurrentUser,
    pagination: PaginationParams = Depends(get_pagination),
    status_filter: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get user's test results history"""
    # Build query
    query = select(TestSession).where(
        and_(
            TestSession.user_id == user.id,
            TestSession.status == TestStatus.COMPLETED
        )
    )
    
    if status_filter:
        query = query.where(TestSession.overall_status == status_filter)
    
    if from_date:
        query = query.where(TestSession.completed_at >= from_date)
    
    if to_date:
        query = query.where(TestSession.completed_at <= to_date)
    
    # Get total count
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0
    
    # Get paginated results
    query = query.order_by(TestSession.completed_at.desc())
    query = query.offset(pagination.offset).limit(pagination.limit)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    items = [
        ResultHistoryItem(
            session_id=s.id,
            completed_at=s.completed_at,
            overall_status=s.overall_status or "unknown",
            tests_count=len(s.results),
            duration_seconds=s.duration_seconds,
            pdf_url=s.pdf_url
        )
        for s in sessions
    ]
    
    return ResultsHistoryResponse(
        items=items,
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.get(
    "/results/{session_id}",
    response_model=DetailedResultResponse,
    summary="Get detailed results",
    description="Get detailed results for a specific session"
)
async def get_detailed_results(
    session_id: UUID,
    user: OptionalUser,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed results for a session"""
    # Get session
    result = await db.execute(
        select(TestSession).where(TestSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test sessiyasi topilmadi"
        )
    
    # Check access (owner or anonymous session)
    if session.user_id and user and session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu natijalarni ko'rish huquqi yo'q"
        )
    
    # Get results
    results_query = await db.execute(
        select(TestResult)
        .where(TestResult.session_id == session_id)
        .order_by(TestResult.test_order)
    )
    results = results_query.scalars().all()
    
    # Build response
    result_items = [
        TestResultWithName(
            id=r.id,
            session_id=r.session_id,
            test_type=r.test_type,
            test_order=r.test_order,
            eye_side=r.eye_side,
            score=r.score,
            status=r.status,
            details=r.details,
            duration_seconds=r.duration_seconds,
            created_at=r.created_at,
            test_name=TEST_NAMES_UZ.get(r.test_type.value, r.test_type.value)
        )
        for r in results
    ]
    
    return DetailedResultResponse(
        session=TestSessionResponse.model_validate(session),
        results=result_items,
        summary=SessionSummary(
            overall_status=session.overall_status or "unknown",
            tests_completed=len(results),
            concerns=session.concerns or [],
            recommendations=session.recommendations or []
        ),
        pdf_url=session.pdf_url
    )


# ==============================================================================
# PDF Download
# ==============================================================================

@router.get(
    "/sessions/{session_id}/pdf",
    summary="Download PDF report",
    description="Download PDF report for a test session"
)
async def download_pdf(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Download PDF report.
    TODO: Implement actual PDF generation and streaming
    """
    result = await db.execute(
        select(TestSession).where(TestSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test sessiyasi topilmadi"
        )
    
    if not session.pdf_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF hisobot hali tayyor emas"
        )
    
    # TODO: Return actual PDF file
    return {"pdf_url": session.pdf_url}
