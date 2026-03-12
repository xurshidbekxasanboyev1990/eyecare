"""
==============================================================================
EyeCare Backend - Redis Cache Manager
==============================================================================
Redis connection and caching utilities for session management and rate limiting.
"""

import json
from typing import Any, Optional, Union
from datetime import timedelta
import redis.asyncio as redis
from loguru import logger

from app.core.config import settings


# ==============================================================================
# Redis Connection Pool
# ==============================================================================

class RedisManager:
    """
    Redis connection manager with async support.
    Provides caching, session storage, and rate limiting.
    """
    
    def __init__(self):
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """Initialize Redis connection pool"""
        try:
            self._pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=20,
                decode_responses=True
            )
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._client.ping()
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def close(self) -> None:
        """Close Redis connection - alias for disconnect"""
        await self.disconnect()
    
    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Redis connection closed")
    
    @property
    def client(self) -> redis.Redis:
        """Get Redis client instance"""
        if self._client is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._client
    
    # ==========================================================================
    # Basic Operations
    # ==========================================================================
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        return await self.client.get(key)
    
    async def set(
        self,
        key: str,
        value: Union[str, int, float],
        expire: Optional[int] = None,
        expire_timedelta: Optional[timedelta] = None
    ) -> bool:
        """
        Set key-value pair with optional expiration.
        
        Args:
            key: Cache key
            value: Value to store
            expire: Expiration in seconds
            expire_timedelta: Expiration as timedelta
            
        Returns:
            True if successful
        """
        ex = expire
        if expire_timedelta:
            ex = int(expire_timedelta.total_seconds())
        
        return await self.client.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> int:
        """Delete key"""
        return await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.client.exists(key) > 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        return await self.client.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        """Get time-to-live for key"""
        return await self.client.ttl(key)
    
    # ==========================================================================
    # JSON Operations
    # ==========================================================================
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get and deserialize JSON value"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Serialize and set JSON value"""
        return await self.set(key, json.dumps(value), expire=expire)
    
    # ==========================================================================
    # Hash Operations (for complex objects)
    # ==========================================================================
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field"""
        return await self.client.hget(name, key)
    
    async def hset(self, name: str, key: str, value: str) -> int:
        """Set hash field"""
        return await self.client.hset(name, key, value)
    
    async def hgetall(self, name: str) -> dict:
        """Get all hash fields"""
        return await self.client.hgetall(name)
    
    async def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields"""
        return await self.client.hdel(name, *keys)
    
    # ==========================================================================
    # List Operations (for queues)
    # ==========================================================================
    
    async def lpush(self, key: str, *values: str) -> int:
        """Push to list head"""
        return await self.client.lpush(key, *values)
    
    async def rpush(self, key: str, *values: str) -> int:
        """Push to list tail"""
        return await self.client.rpush(key, *values)
    
    async def lpop(self, key: str) -> Optional[str]:
        """Pop from list head"""
        return await self.client.lpop(key)
    
    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get list range"""
        return await self.client.lrange(key, start, end)
    
    async def llen(self, key: str) -> int:
        """Get list length"""
        return await self.client.llen(key)
    
    # ==========================================================================
    # Rate Limiting
    # ==========================================================================
    
    async def rate_limit_check(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check rate limit using sliding window.
        
        Args:
            key: Rate limit key (e.g., "rate:user:123")
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        current = await self.client.incr(key)
        
        if current == 1:
            await self.client.expire(key, window_seconds)
        
        remaining = max(0, max_requests - current)
        is_allowed = current <= max_requests
        
        return is_allowed, remaining
    
    # ==========================================================================
    # Session Management
    # ==========================================================================
    
    async def set_session(
        self,
        session_id: str,
        data: dict,
        expire_seconds: int = 3600
    ) -> bool:
        """Store session data"""
        key = f"session:{session_id}"
        return await self.set_json(key, data, expire=expire_seconds)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session data"""
        key = f"session:{session_id}"
        return await self.get_json(key)
    
    async def delete_session(self, session_id: str) -> int:
        """Delete session"""
        key = f"session:{session_id}"
        return await self.delete(key)
    
    # ==========================================================================
    # Telegram Bot State Management
    # ==========================================================================
    
    async def set_bot_state(
        self,
        telegram_id: int,
        state: str,
        data: Optional[dict] = None,
        expire_seconds: int = 86400  # 24 hours
    ) -> bool:
        """Store Telegram bot user state"""
        key = f"bot:state:{telegram_id}"
        state_data = {
            "state": state,
            "data": data or {}
        }
        return await self.set_json(key, state_data, expire=expire_seconds)
    
    async def get_bot_state(self, telegram_id: int) -> Optional[dict]:
        """Get Telegram bot user state"""
        key = f"bot:state:{telegram_id}"
        return await self.get_json(key)
    
    async def clear_bot_state(self, telegram_id: int) -> int:
        """Clear Telegram bot user state"""
        key = f"bot:state:{telegram_id}"
        return await self.delete(key)
    
    # ==========================================================================
    # Verification Codes
    # ==========================================================================
    
    async def set_verification_code(
        self,
        phone: str,
        code: str,
        expire_seconds: int = 300  # 5 minutes
    ) -> bool:
        """Store phone verification code"""
        key = f"verify:{phone}"
        return await self.set(key, code, expire=expire_seconds)
    
    async def get_verification_code(self, phone: str) -> Optional[str]:
        """Get phone verification code"""
        key = f"verify:{phone}"
        return await self.get(key)
    
    async def delete_verification_code(self, phone: str) -> int:
        """Delete verification code after successful verification"""
        key = f"verify:{phone}"
        return await self.delete(key)
    
    # ==========================================================================
    # Cache Operations
    # ==========================================================================
    
    async def cache_get(self, cache_key: str) -> Optional[Any]:
        """Get cached value"""
        return await self.get_json(f"cache:{cache_key}")
    
    async def cache_set(
        self,
        cache_key: str,
        value: Any,
        expire_seconds: int = 300  # 5 minutes default
    ) -> bool:
        """Set cached value"""
        return await self.set_json(f"cache:{cache_key}", value, expire=expire_seconds)
    
    async def cache_delete(self, cache_key: str) -> int:
        """Delete cached value"""
        return await self.delete(f"cache:{cache_key}")
    
    async def cache_clear_pattern(self, pattern: str) -> int:
        """Clear all cache keys matching pattern"""
        keys = []
        async for key in self.client.scan_iter(f"cache:{pattern}*"):
            keys.append(key)
        
        if keys:
            return await self.client.delete(*keys)
        return 0


# ==============================================================================
# Global Redis Manager Instance
# ==============================================================================
redis_manager = RedisManager()


# ==============================================================================
# Dependency Injection
# ==============================================================================
async def get_redis() -> RedisManager:
    """Dependency for getting Redis manager"""
    return redis_manager
