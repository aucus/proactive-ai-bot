"""Telegram message sending"""

import logging
from telegram import Bot
from telegram.error import TelegramError
from src.utils.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


async def send_message(text: str, parse_mode: str = "Markdown") -> bool:
    """
    Send message to Telegram
    
    Args:
        text: Message text
        parse_mode: Parse mode (Markdown, HTML, etc.)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
            parse_mode=parse_mode
        )
        logger.info("Message sent successfully")
        return True
    except TelegramError as e:
        logger.error(f"Failed to send message: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def send_message_sync(text: str, parse_mode: str = "Markdown") -> bool:
    """
    Synchronous wrapper for send_message
    
    Args:
        text: Message text
        parse_mode: Parse mode (Markdown, HTML, etc.)
    
    Returns:
        True if successful, False otherwise
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(send_message(text, parse_mode))



