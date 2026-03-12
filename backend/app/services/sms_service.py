"""
EyeCare Backend - SMS Service

SMS xabarlar yuborish (Eskiz.uz, PlayMobile va boshqa providerlar)
"""

import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import hashlib
import json

from app.core.config import settings
from app.core.redis import redis_manager

logger = logging.getLogger(__name__)


class SMSService:
    """
    SMS xabarlar yuborish uchun service
    
    Qo'llab-quvvatlanadigan providerlar:
    - Eskiz.uz
    - PlayMobile
    - Custom HTTP API
    """
    
    def __init__(self):
        self.provider = settings.SMS_PROVIDER
        self.api_url = settings.SMS_API_URL
        self.api_key = settings.SMS_API_KEY
        self.sender_id = settings.SMS_SENDER_ID
        self._token = None
        self._token_expires = None
    
    async def _get_eskiz_token(self) -> str:
        """
        Eskiz.uz uchun token olish
        """
        # Check cache first
        cached_token = await redis_manager.get("eskiz_token")
        if cached_token:
            return cached_token
        
        # Get new token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/auth/login",
                data={
                    "email": settings.SMS_API_EMAIL,
                    "password": settings.SMS_API_PASSWORD
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("data", {}).get("token")
                
                if token:
                    # Cache token for 29 days (Eskiz tokens valid for 30 days)
                    await redis_manager.set(
                        "eskiz_token",
                        token,
                        expire=60 * 60 * 24 * 29
                    )
                    return token
            
            logger.error(f"Failed to get Eskiz token: {response.text}")
            raise Exception("Failed to authenticate with Eskiz")
    
    async def send_sms(
        self,
        phone: str,
        message: str,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        SMS yuborish
        """
        # Normalize phone number
        phone = self._normalize_phone(phone)
        
        if self.provider == "eskiz":
            return await self._send_eskiz(phone, message, callback_url)
        elif self.provider == "playmobile":
            return await self._send_playmobile(phone, message)
        else:
            return await self._send_custom(phone, message)
    
    async def _send_eskiz(
        self,
        phone: str,
        message: str,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Eskiz.uz orqali SMS yuborish
        """
        try:
            token = await self._get_eskiz_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/message/sms/send",
                    headers={"Authorization": f"Bearer {token}"},
                    data={
                        "mobile_phone": phone,
                        "message": message,
                        "from": self.sender_id,
                        "callback_url": callback_url or ""
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message_id": data.get("id"),
                        "status": data.get("status"),
                        "provider": "eskiz"
                    }
                else:
                    logger.error(f"Eskiz SMS failed: {response.text}")
                    return {
                        "success": False,
                        "error": response.text,
                        "provider": "eskiz"
                    }
                    
        except Exception as e:
            logger.error(f"Eskiz SMS error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "eskiz"
            }
    
    async def _send_playmobile(
        self,
        phone: str,
        message: str
    ) -> Dict[str, Any]:
        """
        PlayMobile orqali SMS yuborish
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json={
                        "messages": [{
                            "recipient": phone,
                            "message-id": hashlib.md5(
                                f"{phone}{datetime.utcnow().timestamp()}".encode()
                            ).hexdigest(),
                            "sms": {
                                "originator": self.sender_id,
                                "content": {
                                    "text": message
                                }
                            }
                        }]
                    },
                    headers={
                        "Authorization": f"Basic {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "response": response.json(),
                        "provider": "playmobile"
                    }
                else:
                    return {
                        "success": False,
                        "error": response.text,
                        "provider": "playmobile"
                    }
                    
        except Exception as e:
            logger.error(f"PlayMobile SMS error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "playmobile"
            }
    
    async def _send_custom(
        self,
        phone: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Custom HTTP API orqali SMS yuborish
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json={
                        "phone": phone,
                        "message": message,
                        "api_key": self.api_key
                    }
                )
                
                return {
                    "success": response.status_code == 200,
                    "response": response.json() if response.status_code == 200 else None,
                    "error": response.text if response.status_code != 200 else None,
                    "provider": "custom"
                }
                
        except Exception as e:
            logger.error(f"Custom SMS error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "custom"
            }
    
    def _normalize_phone(self, phone: str) -> str:
        """
        Telefon raqamini normalizatsiya qilish
        """
        # Remove all non-digit characters
        phone = "".join(c for c in phone if c.isdigit())
        
        # Ensure it starts with country code
        if phone.startswith("998"):
            return phone
        elif phone.startswith("8") and len(phone) == 9:
            # Local format: 8XXXXXXXX
            return f"998{phone}"
        elif len(phone) == 9:
            # Without prefix
            return f"998{phone}"
        
        return phone
    
    async def send_otp(
        self,
        phone: str,
        code: str,
        expire_minutes: int = 5
    ) -> Dict[str, Any]:
        """
        OTP kod yuborish
        """
        message = f"EyeCare tasdiqlash kodi: {code}\nKod {expire_minutes} daqiqa amal qiladi."
        
        # Store OTP in Redis
        await redis_manager.set(
            f"otp:{phone}",
            code,
            expire=expire_minutes * 60
        )
        
        return await self.send_sms(phone, message)
    
    async def verify_otp(self, phone: str, code: str) -> bool:
        """
        OTP kodni tekshirish
        """
        phone = self._normalize_phone(phone)
        stored_code = await redis_manager.get(f"otp:{phone}")
        
        if stored_code and stored_code == code:
            # Delete used OTP
            await redis_manager.delete(f"otp:{phone}")
            return True
        
        return False
    
    async def send_appointment_reminder(
        self,
        phone: str,
        doctor_name: str,
        appointment_time: datetime
    ) -> Dict[str, Any]:
        """
        Uchrashuv eslatmasi SMS
        """
        message = (
            f"EyeCare eslatma:\n"
            f"Shifokor: {doctor_name}\n"
            f"Vaqt: {appointment_time.strftime('%d.%m.%Y %H:%M')}\n"
            f"Iltimos, vaqtida keling!"
        )
        
        return await self.send_sms(phone, message)
    
    async def send_test_result_alert(
        self,
        phone: str,
        risk_level: str
    ) -> Dict[str, Any]:
        """
        Test natijasi haqida SMS
        """
        if risk_level == "high":
            message = (
                "⚠️ EyeCare: Ko'z tekshiruvi natijalaringiz YUQORI RISK ko'rsatmoqda. "
                "ZUDLIK BILAN oftalmologga murojaat qiling!"
            )
        elif risk_level == "moderate":
            message = (
                "EyeCare: Ko'z tekshiruvi natijalari o'rtacha. "
                "Yaqin kunlarda oftalmologga murojaat qilishingizni tavsiya etamiz."
            )
        else:
            message = (
                "✅ EyeCare: Ko'z tekshiruvi natijalaringiz yaxshi. "
                "Muntazam tekshiruvni davom ettiring!"
            )
        
        return await self.send_sms(phone, message)
    
    async def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """
        SMS yetkazish statusini tekshirish (Eskiz uchun)
        """
        if self.provider != "eskiz":
            return {"error": "Status check only available for Eskiz"}
        
        try:
            token = await self._get_eskiz_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/message/sms/status/{message_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": response.text}
                    
        except Exception as e:
            return {"error": str(e)}
    
    async def get_balance(self) -> Dict[str, Any]:
        """
        SMS balansni tekshirish (Eskiz uchun)
        """
        if self.provider != "eskiz":
            return {"error": "Balance check only available for Eskiz"}
        
        try:
            token = await self._get_eskiz_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/user/get-limit",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": response.text}
                    
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
sms_service = SMSService()


# Helper functions
async def send_sms(phone: str, message: str) -> Dict[str, Any]:
    """Convenience function for sending SMS"""
    return await sms_service.send_sms(phone, message)


async def send_otp(phone: str, code: str) -> Dict[str, Any]:
    """Convenience function for sending OTP"""
    return await sms_service.send_otp(phone, code)


async def verify_otp(phone: str, code: str) -> bool:
    """Convenience function for verifying OTP"""
    return await sms_service.verify_otp(phone, code)
