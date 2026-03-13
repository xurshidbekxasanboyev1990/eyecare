"""
EyeCare Backend - Core Module
"""

from app.core.config import settings, get_settings
from app.core.database import get_db, Base, engine, init_db, close_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    verify_access_token,
    verify_refresh_token,
    generate_verification_code,
    generate_session_token,
)
from app.core.redis import redis_manager, get_redis

__all__ = [
    # Config
    "settings",
    "get_settings",
    
    # Database
    "get_db",
    "Base",
    "engine",
    "init_db",
    "close_db",
    
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "decode_token",
    "verify_access_token",
    "verify_refresh_token",
    "generate_verification_code",
    "generate_session_token",
    
    # Cache (in-memory)
    "redis_manager",
    "get_redis",
]
