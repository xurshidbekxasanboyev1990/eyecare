"""
EyeCare Backend - Bot Module
"""

from app.bot.handlers import create_bot, start_polling
from app.bot.handlers import router

__all__ = ["create_bot", "start_polling", "router"]
