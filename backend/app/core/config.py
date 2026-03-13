"""
==============================================================================
EyeCare Backend - Configuration Module
==============================================================================
Centralized configuration management using Pydantic Settings.
Loads environment variables with type validation and default values.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json


class Settings(BaseSettings):
    """
    Application Settings - loaded from environment variables.
    Uses .env file in development and system env vars in production.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ==== App Settings ====
    APP_NAME: str = "EyeCare"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-this-secret-key-in-production"
    UPLOAD_DIR: str = "./uploads"
    
    # ==== Server ====
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # ==== Database ====
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/eyecare"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # ==== JWT ====
    JWT_SECRET_KEY: str = "jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # ==== Telegram Bot ====
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_WEBAPP_URL: str = "https://eyecare.uz"
    TELEGRAM_BOT_USERNAME: str = "eyecare_bot"
    
    # Aliases for backward compatibility
    @property
    def bot_token(self) -> str:
        return self.TELEGRAM_BOT_TOKEN
    
    @property
    def bot_webhook_url(self) -> str:
        return self.TELEGRAM_WEBHOOK_URL
    
    @property
    def bot_webhook_secret(self) -> str:
        return self.SECRET_KEY[:32]
    
    # ==== Admin ====
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "eyecare2026"
    ADMIN_EMAIL: str = "admin@eyecare.uz"
    
    # ==== SMS Provider ====
    SMS_PROVIDER: str = "eskiz"  # eskiz, playmobile, custom
    SMS_API_URL: str = "https://notify.eskiz.uz/api"
    SMS_API_KEY: str = ""
    SMS_API_EMAIL: str = ""
    SMS_API_PASSWORD: str = ""
    SMS_SENDER_ID: str = "EyeCare"
    
    # ==== Storage ====
    STORAGE_ENDPOINT: str = "localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET: str = "eyecare"
    STORAGE_USE_SSL: bool = False
    
    # ==== CORS ====
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "*"]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string or list"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v
    
    # ==== Test Distances ====
    TEST_DISTANCE_SNELLEN: float = 5.0  # meters
    TEST_DISTANCE_ISHIHARA: float = 0.75  # meters
    TEST_DISTANCE_ASTIGMATISM: float = 0.5  # meters
    TEST_DISTANCE_AMSLER: float = 0.3  # meters
    
    # ==== Rate Limiting ====
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # ==== Computed Properties ====
    @property
    def storage_url(self) -> str:
        """Get full storage URL"""
        protocol = "https" if self.STORAGE_USE_SSL else "http"
        return f"{protocol}://{self.STORAGE_ENDPOINT}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses LRU cache to ensure settings are loaded only once.
    """
    return Settings()


# Global settings instance for easy import
settings = get_settings()


# ==============================================================================
# Test Configuration
# ==============================================================================

# Test types and their required distances (in cm)
TEST_DISTANCES = {
    "visual_acuity": 300,      # 3 meters (Snellen)
    "color_blindness": 75,     # 75 cm (Ishihara)
    "amsler_grid": 30,         # 30 cm
    "contrast": 100,           # 1 meter
    "astigmatism": 50,         # 50 cm
    "duochrome": 50,           # 50 cm
    "near_vision": 35,         # 35 cm
    "red_desaturation": 50,    # 50 cm
    "perimetry": 50,           # 50 cm
    "dry_eye": 40,             # 40 cm
    "glaucoma": 50,            # 50 cm (for bot)
    "cataract": 50,            # 50 cm (for bot)
    "myopia": 500,             # 5 meters (for bot)
    "chorioretinitis": 50,     # 50 cm (for bot)
    "retinal_dystrophy": 30,   # 30 cm (for bot)
}

# Test names in Uzbek
TEST_NAMES_UZ = {
    "visual_acuity": "Ko'rish O'tkirligi",
    "color_blindness": "Rang Ajratish (Daltonizm)",
    "amsler_grid": "Amsler Panjarasi",
    "contrast": "Kontrast Sezgirlik",
    "astigmatism": "Astigmatizm",
    "duochrome": "Duoxrom",
    "near_vision": "Yaqindan Ko'rish",
    "red_desaturation": "Qizil Desaturatsiya",
    "perimetry": "Perimetriya",
    "dry_eye": "Quruq Ko'z Sindromi",
    "glaucoma": "Glaukoma",
    "cataract": "Katarakta",
    "myopia": "Miopiya",
    "chorioretinitis": "Xorioretinit",
    "retinal_dystrophy": "To'r Parda Distrofiyasi",
}

# Disease-specific medication recommendations
MEDICATION_RECOMMENDATIONS = {
    "myopia": {
        "medications": ["Tauforuch 4%", "Glafand"],
        "description": "Ko'z to'qimalarini oziqlantirish uchun",
        "usage": "Kuniga 3 marta, 1-2 tomchi"
    },
    "chorioretinitis": {
        "medications": ["Deksametazon (tomchi)", "Retinamamin (og'riq bo'lsa)"],
        "description": "Yallig'lanishni kamaytirish uchun",
        "usage": "Shifokor ko'rsatmasiga binoan"
    },
    "retinal_dystrophy": {
        "medications": ["Retinamamin"],
        "description": "To'r parda yemirilishini to'xtatish uchun",
        "usage": "Kuniga 2 marta"
    },
    "glaucoma": {
        "medications": ["Timonil 1%", "Arutimol 0.5%"],
        "description": "Ko'z ichki bosimini tushirish uchun",
        "usage": "Kuniga 2 marta, ertalab va kechqurun"
    },
    "cataract": {
        "medications": ["Quinax", "Taufon"],
        "description": "Linza xiralashuvini sekinlashtirish uchun",
        "usage": "Kuniga 3-4 marta"
    }
}

# Disclaimer message
DISCLAIMER_MESSAGE = """
⚠️ MUHIM ESLATMA:
Ushbu tavsiyalar doktor tomonidan yozilgan varoq asosida berildi. 
Yakuniy qarorni shifokoringiz bilan maslahatlashing.
O'z-o'zini davolash xavfli bo'lishi mumkin!
"""
