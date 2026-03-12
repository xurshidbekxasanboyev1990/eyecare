"""
EyeCare Backend - Notification Service

Push bildirishnomalar va Telegram xabarlar
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import logging

from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationChannel
from app.models.user import User
from app.models.telegram import TelegramSession
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Bildirishnomalar bilan ishlash uchun service
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._telegram_bot = None
    
    def set_telegram_bot(self, bot):
        """Telegram bot instance'ni set qilish"""
        self._telegram_bot = bot
    
    async def create_notification(
        self,
        user_id,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.SYSTEM,
        data: Optional[Dict[str, Any]] = None,
        channel: NotificationChannel = NotificationChannel.PUSH
    ) -> Notification:
        """
        Yangi bildirishnoma yaratish
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            body=message,
            type=notification_type,
            channel=channel,
            data=data or {},
            status=NotificationStatus.PENDING
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    async def get_user_notifications(
        self,
        user_id,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[Notification]:
        """
        Foydalanuvchi bildirishnomalarini olish
        """
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.read_at.is_(None))
        
        query = query.order_by(Notification.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def mark_as_read(self, notification_id) -> bool:
        """
        Bildirishnomani o'qilgan deb belgilash
        """
        await self.db.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(
                read_at=datetime.utcnow(),
                status=NotificationStatus.READ
            )
        )
        await self.db.commit()
        return True
    
    async def mark_all_as_read(self, user_id) -> int:
        """
        Barcha bildirishnomalarni o'qilgan deb belgilash
        """
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None)
            )
            .values(
                read_at=datetime.utcnow(),
                status=NotificationStatus.READ
            )
        )
        await self.db.commit()
        return result.rowcount
    
    async def get_unread_count(self, user_id) -> int:
        """
        O'qilmagan bildirishnomalar sonini olish
        """
        from sqlalchemy import func
        
        result = await self.db.execute(
            select(func.count(Notification.id))
            .where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None)
            )
        )
        return result.scalar() or 0
    
    async def send_push_notification(
        self,
        user_id,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Push bildirishnoma yuborish (Firebase)
        
        TODO: Firebase Cloud Messaging integratsiyasi
        """
        # Create notification record first
        await self.create_notification(
            user_id=user_id,
            title=title,
            message=body,
            notification_type=NotificationType.SYSTEM,
            channel=NotificationChannel.PUSH,
            data=data
        )
        
        # Get user's FCM token
        result = await self.db.execute(
            select(User.fcm_token).where(User.id == user_id)
        )
        fcm_token = result.scalar()
        
        if not fcm_token:
            logger.warning(f"No FCM token for user {user_id}")
            return False
        
        # TODO: Implement actual FCM push
        # For now, just log
        logger.info(f"Would send push to {user_id}: {title} - {body}")
        return True
    
    async def send_telegram_notification(
        self,
        telegram_id: int,
        message: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[Any] = None
    ) -> bool:
        """
        Telegram orqali xabar yuborish
        """
        if not self._telegram_bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            await self._telegram_bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message to {telegram_id}: {e}")
            return False
    
    async def notify_user(
        self,
        user_id,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.SYSTEM,
        channels: List[str] = None
    ) -> Dict[str, bool]:
        """
        Foydalanuvchiga barcha kanallarda bildirishnoma yuborish
        """
        if channels is None:
            channels = ["app", "telegram"]
        
        results = {}
        
        # Create in-app notification
        if "app" in channels:
            await self.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type
            )
            results["app"] = True
        
        # Send push notification
        if "push" in channels:
            results["push"] = await self.send_push_notification(
                user_id=user_id,
                title=title,
                body=message
            )
        
        # Send Telegram notification
        if "telegram" in channels:
            # Get user's Telegram ID
            result = await self.db.execute(
                select(TelegramSession.telegram_id)
                .where(TelegramSession.user_id == user_id)
            )
            telegram_id = result.scalar()
            
            if telegram_id:
                results["telegram"] = await self.send_telegram_notification(
                    telegram_id=telegram_id,
                    message=f"<b>{title}</b>\n\n{message}"
                )
            else:
                results["telegram"] = False
        
        return results
    
    async def send_bulk_notification(
        self,
        user_ids: List,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.SYSTEM
    ) -> Dict[str, Any]:
        """
        Ko'p foydalanuvchilarga bildirishnoma yuborish
        """
        results = {
            "total": len(user_ids),
            "success": 0,
            "failed": 0
        }
        
        for user_id in user_ids:
            try:
                await self.notify_user(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=notification_type
                )
                results["success"] += 1
            except Exception as e:
                logger.error(f"Failed to notify user {user_id}: {e}")
                results["failed"] += 1
        
        return results
    
    async def send_appointment_reminder(
        self,
        user_id,
        doctor_name: str,
        appointment_time: datetime
    ) -> bool:
        """
        Uchrashuv eslatmasi yuborish
        """
        title = "🗓️ Uchrashuv eslatmasi"
        message = (
            f"Sizning uchrashuvingiz:\n"
            f"👨‍⚕️ Shifokor: {doctor_name}\n"
            f"📅 Vaqt: {appointment_time.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"Iltimos, vaqtida keling!"
        )
        
        result = await self.notify_user(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.APPOINTMENT,
            channels=["app", "telegram", "push"]
        )
        
        return all(result.values())
    
    async def send_test_result_notification(
        self,
        user_id,
        overall_score: float,
        risk_level: str
    ) -> bool:
        """
        Test natijasi haqida xabar yuborish
        """
        if risk_level == "high":
            emoji = "🔴"
            urgency = "ZUDLIK BILAN"
        elif risk_level == "moderate":
            emoji = "🟡"
            urgency = "tezroq"
        else:
            emoji = "🟢"
            urgency = ""
        
        title = f"{emoji} Test natijalari tayyor"
        message = (
            f"📊 Sizning umumiy ballingiz: {overall_score}/100\n"
            f"⚡ Risk darajasi: {risk_level.upper()}\n\n"
        )
        
        if urgency:
            message += f"⚠️ {urgency} oftalmologga murojaat qiling!"
        else:
            message += "✅ Yaxshi natija! Muntazam tekshiruvni davom ettiring."
        
        result = await self.notify_user(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.RESULT,
            channels=["app", "telegram"]
        )
        
        return all(result.values())
    
    async def delete_old_notifications(self, days: int = 30) -> int:
        """
        Eski bildirishnomalarni o'chirish
        """
        from sqlalchemy import delete
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            delete(Notification)
            .where(
                Notification.created_at < cutoff_date,
                Notification.read_at.isnot(None)
            )
        )
        await self.db.commit()
        
        return result.rowcount


# Required import
from datetime import timedelta


# Factory function
def get_notification_service(db: AsyncSession) -> NotificationService:
    return NotificationService(db)
