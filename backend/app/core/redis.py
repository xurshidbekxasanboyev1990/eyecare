"""
==============================================================================
EyeCare Backend - In-Memory Cache Manager (Redis-free)
==============================================================================
In-memory caching utilities for session management and rate limiting.
No external Redis dependency required.
"""

import json
import time
import asyncio
from typing import Any, Optional, Union
from datetime import timedelta
from loguru import logger

from app.core.config import settings


# ==============================================================================
# In-Memory Storage (Redis replacement)
# ==============================================================================

class RedisManager:
    """
    In-memory cache manager (Redis-free).
    Provides caching, session storage, and rate limiting using dict-based storage.
    """
    
    def __init__(self):
        self._store: dict[str, Any] = {}
        self._expiry: dict[str, float] = {}
        self._connected = False
    
    async def connect(self) -> None:
        """Initialize in-memory storage"""
        self._store = {}
        self._expiry = {}
        self._connected = True
        logger.info("✅ In-memory cache initialized (no Redis)")
    
    async def close(self) -> None:
        """Close - alias for disconnect"""
        await self.disconnect()
    
    async def disconnect(self) -> None:
        """Clear in-memory storage"""
        self._store.clear()
        self._expiry.clear()
        self._connected = False
        logger.info("In-memory cache cleared")
    
    def _is_expired(self, key: str) -> bool:
        """Check if key is expired"""
        if key in self._expiry:
            if time.time() > self._expiry[key]:
                self._store.pop(key, None)
                self._expiry.pop(key, None)
                return True
        return False
    
    # ==========================================================================
    # Basic Operations
    # ==========================================================================
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if self._is_expired(key):
            return None
        return self._store.get(key)
    
    async def set(
        self,
        key: str,
        value: Union[str, int, float],
        expire: Optional[int] = None,
        expire_timedelta: Optional[timedelta] = None
    ) -> bool:
        """Set key-value pair with optional expiration."""
        self._store[key] = str(value)
        ex = expire
        if expire_timedelta:
            ex = int(expire_timedelta.total_seconds())
        if ex:
            self._expiry[key] = time.time() + ex
        return True
    
    async def delete(self, key: str) -> int:
        """Delete key"""
        removed = 1 if key in self._store else 0
        self._store.pop(key, None)
        self._expiry.pop(key, None)
        return removed
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if self._is_expired(key):
            return False
        return key in self._store
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        if key in self._store:
            self._expiry[key] = time.time() + seconds
            return True
        return False
    
    async def ttl(self, key: str) -> int:
        """Get time-to-live for key"""
        if key in self._expiry:
            remaining = int(self._expiry[key] - time.time())
            return max(remaining, -1)
        return -1
    
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
        h = self._store.get(name, {})
        if isinstance(h, dict):
            return h.get(key)
        return None
    
    async def hset(self, name: str, key: str, value: str) -> int:
        """Set hash field"""
        if name not in self._store or not isinstance(self._store[name], dict):
            self._store[name] = {}
        self._store[name][key] = value
        return 1
    
    async def hgetall(self, name: str) -> dict:
        """Get all hash fields"""
        h = self._store.get(name, {})
        return h if isinstance(h, dict) else {}
    
    async def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields"""
        h = self._store.get(name, {})
        if isinstance(h, dict):
            count = 0
            for k in keys:
                if k in h:
                    del h[k]
                    count += 1
            return count
        return 0
    
    # ==========================================================================
    # List Operations (for queues)
    # ==========================================================================
    
    async def lpush(self, key: str, *values: str) -> int:
        """Push to list head"""
        if key not in self._store or not isinstance(self._store[key], list):
            self._store[key] = []
        for v in values:
            self._store[key].insert(0, v)
        return len(self._store[key])
    
    async def rpush(self, key: str, *values: str) -> int:
        """Push to list tail"""
        if key not in self._store or not isinstance(self._store[key], list):
            self._store[key] = []
        self._store[key].extend(values)
        return len(self._store[key])
    
    async def lpop(self, key: str) -> Optional[str]:
        """Pop from list head"""
        lst = self._store.get(key, [])
        if isinstance(lst, list) and lst:
            return lst.pop(0)
        return None
    
    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get list range"""
        lst = self._store.get(key, [])
        if isinstance(lst, list):
            if end == -1:
                return lst[start:]
            return lst[start:end + 1]
        return []
    
    async def llen(self, key: str) -> int:
        """Get list length"""
        lst = self._store.get(key, [])
        return len(lst) if isinstance(lst, list) else 0
    
    # ==========================================================================
    # Rate Limiting
    # ==========================================================================
    
    async def rate_limit_check(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple:
        """
        Check rate limit using simple counter.
        
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        if self._is_expired(key):
            pass  # key was cleaned up
        
        current_str = self._store.get(key)
        if current_str is None:
            current = 1
        else:
            current = int(current_str) + 1
        
        self._store[key] = str(current)
        if current == 1:
            self._expiry[key] = time.time() + window_seconds
        
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
        expire_seconds: int = 86400
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
        expire_seconds: int = 300
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
        expire_seconds: int = 300
    ) -> bool:
        """Set cached value"""
        return await self.set_json(f"cache:{cache_key}", value, expire=expire_seconds)
    
    async def cache_delete(self, cache_key: str) -> int:
        """Delete cached value"""
        return await self.delete(f"cache:{cache_key}")
    
    async def cache_clear_pattern(self, pattern: str) -> int:
        """Clear all cache keys matching pattern"""
        prefix = f"cache:{pattern}"
        keys_to_delete = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_delete:
            self._store.pop(k, None)
            self._expiry.pop(k, None)
        return len(keys_to_delete)


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
