"""Telegram bot polling service"""

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.utils.config import TELEGRAM_TOKEN
from src.bot.handlers import (
    start_command,
    help_command,
    weather_command_handler,
    news_command_handler,
    schedule_command_handler,
    project_command_handler,
    settings_command_handler,
    unknown_command
)

logger = logging.getLogger(__name__)


def setup_handlers(application: Application):
    """Setup command handlers"""
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("weather", weather_command_handler))
    application.add_handler(CommandHandler("news", news_command_handler))
    application.add_handler(CommandHandler("schedule", schedule_command_handler))
    application.add_handler(CommandHandler("project", project_command_handler))
    application.add_handler(CommandHandler("settings", settings_command_handler))
    
    # Unknown command handler (must be last)
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))


async def start_polling():
    """Start polling for updates"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not set, cannot start polling")
        return
    
    try:
        # Create application
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Setup handlers
        setup_handlers(application)
        
        logger.info("Starting bot polling...")
        
        # Start polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            poll_interval=5.0,  # Poll every 5 seconds
            timeout=10,
            drop_pending_updates=True
        )
        
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Keep running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("Stopping bot...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
    except Exception as e:
        logger.error(f"Polling error: {e}", exc_info=True)


def run_polling():
    """Run polling in sync mode"""
    asyncio.run(start_polling())

