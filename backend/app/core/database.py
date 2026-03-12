"""
==============================================================================
EyeCare Backend - Database Configuration
==============================================================================
Async SQLAlchemy setup with PostgreSQL for high-performance database operations.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from typing import AsyncGenerator

from app.core.config import settings


# ==============================================================================
# Database Naming Convention (for Alembic migrations)
# ==============================================================================
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


# ==============================================================================
# Base Model Class
# ==============================================================================
class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Includes metadata with naming convention for consistent migrations.
    """
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# ==============================================================================
# Async Engine & Session
# ==============================================================================

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Test connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ==============================================================================
# Dependency Injection
# ==============================================================================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    
    Usage in FastAPI:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    
    Yields:
        AsyncSession: Database session that auto-closes after request.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ==============================================================================
# Database Lifecycle Functions
# ==============================================================================
async def init_db() -> None:
    """
    Initialize database - create all tables.
    Called on application startup.
    """
    async with engine.begin() as conn:
        # Import all models to register them with Base
        from app.models import user, test, doctor, notification, telegram  # noqa
        
        # Create all tables (in development)
        if settings.DEBUG:
            await conn.run_sync(Base.metadata.create_all)


# Alias for main.py
async_session_maker = async_session_factory


async def close_db() -> None:
    """
    Close database connections.
    Called on application shutdown.
    """
    await engine.dispose()


# ==============================================================================
# Health Check
# ==============================================================================
async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        bool: True if connection is healthy, False otherwise.
    """
    try:
        async with async_session_factory() as session:
            await session.execute("SELECT 1")
            return True
    except Exception:
        return False
