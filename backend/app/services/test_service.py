"""
EyeCare Backend - Test Service

Test natijalari va sessiyalarni boshqarish
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.test import TestSession, TestResult, TestType, TestStatus, EyeSide
from app.models.user import User


class TestService:
    """Test natijalari bilan ishlash uchun service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_session(
        self,
        user_id=None,
        source: str = "web",
        ip_address: Optional[str] = None
    ) -> TestSession:
        """
        Yangi test sessiyasi yaratish
        """
        from app.core.security import generate_session_token
        
        session = TestSession(
            user_id=user_id,
            session_token=generate_session_token(),
            source=source,
            ip_address=ip_address
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def get_session(self, session_id) -> Optional[TestSession]:
        """
        Sessiyani ID bo'yicha olish
        """
        result = await self.db.execute(
            select(TestSession)
            .options(selectinload(TestSession.results))
            .where(TestSession.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_sessions(
        self,
        user_id,
        limit: int = 10,
        offset: int = 0
    ) -> List[TestSession]:
        """
        Foydalanuvchi sessiyalarini olish
        """
        result = await self.db.execute(
            select(TestSession)
            .where(TestSession.user_id == user_id)
            .order_by(TestSession.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def add_result(
        self,
        session_id,
        test_type: TestType,
        score: str,
        data: Dict[str, Any],
        eye_side: Optional[EyeSide] = None,
        distance_cm: Optional[float] = None
    ) -> TestResult:
        """
        Test natijasini qo'shish
        """
        test_result = TestResult(
            session_id=session_id,
            test_type=test_type,
            score=str(score),
            raw_data=data,
            eye_side=eye_side or EyeSide.BOTH,
            distance_cm=distance_cm
        )
        
        self.db.add(test_result)
        await self.db.commit()
        await self.db.refresh(test_result)
        
        return test_result
    
    async def complete_session(
        self,
        session_id,
        overall_status: Optional[str] = None,
        recommendations: Optional[List[str]] = None,
        concerns: Optional[List[str]] = None
    ) -> TestSession:
        """
        Sessiyani yakunlash
        """
        update_values = {
            "completed_at": datetime.utcnow(),
            "status": TestStatus.COMPLETED
        }
        
        if overall_status:
            update_values["overall_status"] = overall_status
        if recommendations:
            update_values["recommendations"] = recommendations
        if concerns:
            update_values["concerns"] = concerns
        
        # Update session
        await self.db.execute(
            update(TestSession)
            .where(TestSession.id == session_id)
            .values(**update_values)
        )
        
        await self.db.commit()
        
        # Return updated session
        return await self.get_session(session_id)
    
    async def get_session_results(self, session_id) -> List[TestResult]:
        """
        Sessiya natijalarini olish
        """
        result = await self.db.execute(
            select(TestResult)
            .where(TestResult.session_id == session_id)
            .order_by(TestResult.created_at)
        )
        return list(result.scalars().all())
    
    async def calculate_overall_score(self, session_id) -> float:
        """
        Umumiy ball hisoblash
        """
        results = await self.get_session_results(session_id)
        
        if not results:
            return 0.0
        
        total_score = 0.0
        count = 0
        for r in results:
            try:
                total_score += float(r.score)
                count += 1
            except (ValueError, TypeError):
                pass
        
        return round(total_score / count, 2) if count > 0 else 0.0
    
    async def get_test_statistics(self, user_id) -> Dict[str, Any]:
        """
        Foydalanuvchi test statistikasi
        """
        sessions = await self.get_user_sessions(user_id, limit=100)
        
        if not sessions:
            return {
                "total_sessions": 0,
                "completed_sessions": 0,
                "average_score": 0,
                "tests_by_type": {}
            }
        
        completed = [s for s in sessions if s.completed_at]
        
        # Get all results for these sessions
        session_ids = [s.id for s in sessions]
        result = await self.db.execute(
            select(TestResult)
            .where(TestResult.session_id.in_(session_ids))
        )
        all_results = list(result.scalars().all())
        
        # Calculate stats
        tests_by_type = {}
        total_score = 0
        
        for r in all_results:
            test_type = r.test_type.value
            if test_type not in tests_by_type:
                tests_by_type[test_type] = {"count": 0, "total_score": 0}
            tests_by_type[test_type]["count"] += 1
            try:
                score_val = float(r.score)
                tests_by_type[test_type]["total_score"] += score_val
                total_score += score_val
            except (ValueError, TypeError):
                pass
        
        # Calculate averages
        for test_type in tests_by_type:
            count = tests_by_type[test_type]["count"]
            total = tests_by_type[test_type]["total_score"]
            tests_by_type[test_type]["average"] = round(total / count, 2) if count > 0 else 0
        
        return {
            "total_sessions": len(sessions),
            "completed_sessions": len(completed),
            "average_score": round(total_score / len(all_results), 2) if all_results else 0,
            "tests_by_type": tests_by_type
        }
    
    async def delete_session(self, session_id) -> bool:
        """
        Sessiyani o'chirish
        """
        session = await self.get_session(session_id)
        if not session:
            return False
        
        await self.db.delete(session)
        await self.db.commit()
        return True


# Singleton instance creator
def get_test_service(db: AsyncSession) -> TestService:
    return TestService(db)
