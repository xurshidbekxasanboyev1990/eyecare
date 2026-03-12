"""
==============================================================================
EyeCare Backend - Security & Authentication
==============================================================================
JWT token handling, password hashing, and security utilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import jwt, JWTError
from pydantic import BaseModel
import secrets
import hashlib
import bcrypt

from app.core.config import settings


# ==============================================================================
# Password Hashing (Direct bcrypt - no passlib)
# ==============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    # Truncate password to 72 bytes (bcrypt limit)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


# Alias for compatibility
get_password_hash = hash_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# ==============================================================================
# JWT Token Models
# ==============================================================================

class TokenPayload(BaseModel):
    """JWT Token payload structure"""
    sub: str  # Subject (user_id)
    type: str  # Token type: "access" or "refresh"
    exp: datetime  # Expiration time
    iat: datetime  # Issued at time
    jti: Optional[str] = None  # JWT ID for token revocation


class TokenPair(BaseModel):
    """Access and refresh token pair"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Access token expiry in seconds


# ==============================================================================
# JWT Token Functions
# ==============================================================================

def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: User ID or identifier
        expires_delta: Custom expiration time
        additional_claims: Extra data to include in token
        
    Returns:
        Encoded JWT token string
    """
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "type": "access",
        "exp": expire,
        "iat": now,
        "jti": secrets.token_hex(16)
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: User ID or identifier
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT refresh token string
    """
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": str(subject),
        "type": "refresh",
        "exp": expire,
        "iat": now,
        "jti": secrets.token_hex(16)
    }
    
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def create_token_pair(subject: Union[str, int]) -> TokenPair:
    """
    Create both access and refresh tokens.
    
    Args:
        subject: User ID or identifier
        
    Returns:
        TokenPair with access and refresh tokens
    """
    access_token = create_access_token(subject)
    refresh_token = create_refresh_token(subject)
    
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenPayload if valid, None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenPayload(**payload)
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[str]:
    """
    Verify an access token and return the user ID.
    
    Args:
        token: JWT access token
        
    Returns:
        User ID if valid, None if invalid
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    if payload.type != "access":
        return None
    
    return payload.sub


def verify_refresh_token(token: str) -> Optional[str]:
    """
    Verify a refresh token and return the user ID.
    
    Args:
        token: JWT refresh token
        
    Returns:
        User ID if valid, None if invalid
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    if payload.type != "refresh":
        return None
    
    return payload.sub


# ==============================================================================
# Utility Functions
# ==============================================================================

def generate_verification_code(length: int = 6) -> str:
    """
    Generate a numeric verification code.
    
    Args:
        length: Number of digits
        
    Returns:
        Random numeric code string
    """
    return "".join([str(secrets.randbelow(10)) for _ in range(length)])


def generate_session_token(length: int = 32) -> str:
    """
    Generate a secure session token.
    
    Args:
        length: Token length in bytes
        
    Returns:
        Hex-encoded random token
    """
    return secrets.token_hex(length)


def generate_api_key() -> str:
    """
    Generate a secure API key.
    
    Returns:
        API key string with prefix
    """
    return f"eyecare_{secrets.token_hex(24)}"


def hash_token(token: str) -> str:
    """
    Create a hash of a token for secure storage.
    
    Args:
        token: Token to hash
        
    Returns:
        SHA256 hash of token
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify webhook signature (HMAC-SHA256).
    
    Args:
        payload: Raw request body
        signature: Provided signature
        secret: Webhook secret
        
    Returns:
        True if signature is valid
    """
    import hmac
    
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)
