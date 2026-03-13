"""
EyeCare Backend - Main Application Entry Point

FastAPI ilova va barcha componentlarni birlashtirish
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import os
import asyncio
import time
from datetime import datetime

from app.core.config import settings
from app.core.database import engine, Base, async_session_maker
from app.core.redis import redis_manager
from app.api import api_router

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot instance
bot = None
dp = None
bot_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Startup va shutdown eventlarini boshqarish
    """
    global bot, dp, bot_task
    
    logger.info("Starting EyeCare Backend...")
    
    # Initialize in-memory cache
    try:
        await redis_manager.connect()
        logger.info("✅ Cache initialized")
    except Exception as e:
        logger.error(f"❌ Cache initialization failed: {e}")
    
    # NOTE: DB tables are created by Alembic migrations (entrypoint.sh)
    # create_all is NOT called here to avoid conflicts with Alembic
    
    # Seed default admin from environment (if not exists)
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT id FROM admins WHERE username = :u LIMIT 1"),
                {"u": settings.ADMIN_USERNAME}
            )
            if not result.fetchone():
                from app.core.security import get_password_hash
                admin_hash = get_password_hash(settings.ADMIN_PASSWORD)
                await conn.execute(
                    text("""
                        INSERT INTO admins (id, username, email, password_hash, full_name, is_active, created_at)
                        VALUES (gen_random_uuid(), :u, :e, :h, :n, true, NOW())
                        ON CONFLICT (username) DO NOTHING
                    """),
                    {"u": settings.ADMIN_USERNAME, "e": settings.ADMIN_EMAIL,
                     "h": admin_hash, "n": "Administrator"}
                )
                logger.info(f"✅ Default admin created: {settings.ADMIN_USERNAME}")
            else:
                logger.info("✅ Admin already exists")
    except Exception as e:
        logger.error(f"❌ Admin seed failed: {e}")
    
    # Create upload directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "avatars"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "reports"), exist_ok=True)
    logger.info("✅ Upload directories created")
    
    # Initialize Telegram Bot
    if settings.TELEGRAM_BOT_TOKEN:
        try:
            from app.bot.handlers import create_bot, start_polling
            bot, dp = await create_bot()
            
            if settings.TELEGRAM_WEBHOOK_URL:
                # Production: Use webhook
                await bot.set_webhook(
                    url=settings.TELEGRAM_WEBHOOK_URL,
                    secret_token=settings.bot_webhook_secret
                )
                logger.info(f"✅ Telegram bot webhook set: {settings.TELEGRAM_WEBHOOK_URL}")
            else:
                # Development: Use polling
                async def run_bot():
                    await dp.start_polling(bot)
                bot_task = asyncio.create_task(run_bot())
                logger.info("✅ Telegram bot polling started")
                
        except Exception as e:
            logger.error(f"❌ Telegram bot initialization failed: {e}")
    else:
        logger.warning("⚠️ Telegram bot token not configured")
    
    logger.info("🚀 EyeCare Backend started successfully!")
    
    yield  # Application is running
    
    # Shutdown
    logger.info("Shutting down EyeCare Backend...")
    
    # Stop bot polling
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
    
    # Close cache
    await redis_manager.close()
    
    # Close database connections
    await engine.dispose()
    
    logger.info("👋 EyeCare Backend stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    EyeCare Backend API
    
    Ko'z salomatligi tekshirish platformasi uchun backend API.
    
    ## Imkoniyatlar
    
    * 🔐 **Autentifikatsiya** - JWT token asosida
    * 👤 **Foydalanuvchilar** - Ro'yxatdan o'tish, profil boshqaruvi
    * 🩺 **Testlar** - 10 xil ko'z testi
    * 👨‍⚕️ **Shifokorlar** - Ro'yxat, uchrashuv belgilash
    * 🤖 **Telegram Bot** - Skrining va natijalar
    * 📱 **PWA** - Web App qo'llab-quvvatlash
    """,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted hosts (production da domenni ko'rsating)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Production: ["eyecare.uz", "www.eyecare.uz"]
    )


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Security headers va request timing"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + "ms"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validation xatolarini chiroyli formatda qaytarish"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation xatosi",
            "errors": errors
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP xatolarini chiroyli formatda qaytarish"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Umumiy xatolarni boshqarish"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Ichki server xatosi" if not settings.DEBUG else str(exc),
            "status_code": 500
        }
    )


# Include API router
app.include_router(api_router, prefix="/api/v1")


# Static files (uploads)
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from sqlalchemy import text
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {}
    }
    
    # Check database
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check in-memory cache
    try:
        await redis_manager.set("health_check", "ok", expire=10)
        health_status["services"]["cache"] = "healthy"
    except Exception as e:
        health_status["services"]["cache"] = f"unhealthy: {str(e)}"
    
    # Check Telegram bot
    if bot:
        health_status["services"]["telegram_bot"] = "running"
    else:
        health_status["services"]["telegram_bot"] = "not configured"
    
    return health_status


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else None,
        "health": "/health"
    }


# Telegram webhook endpoint (production)
@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Telegram webhook endpoint"""
    if not bot or not dp:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    try:
        data = await request.json()
        # Process update
        from aiogram.types import Update
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )
