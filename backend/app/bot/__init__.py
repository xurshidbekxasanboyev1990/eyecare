"""
EyeCare Backend - Bot Module
"""

from app.bot.handlers import create_bot, start_polling

# Placeholder for webhook setup
async def setup_webhook(bot, url):
    """Setup webhook for production mode"""
    if bot:
        await bot.set_webhook(url=url)

# Aiogram router for webhook handling
from app.bot.handlers import router

__all__ = ["create_bot", "start_polling", "setup_webhook", "router"]
