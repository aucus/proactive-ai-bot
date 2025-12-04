"""Monitoring and health check utilities"""

import logging
import time
from typing import Dict, Optional
from datetime import datetime
from src.utils.config import TELEGRAM_TOKEN, GEMINI_API_KEY, OPENWEATHER_API_KEY
from src.bot.telegram import send_message_sync

logger = logging.getLogger(__name__)


def check_health() -> Dict[str, bool]:
    """
    Check health of all services
    
    Returns:
        Dictionary with health status of each service
    """
    health_status = {
        "telegram": bool(TELEGRAM_TOKEN),
        "gemini": bool(GEMINI_API_KEY),
        "weather": bool(OPENWEATHER_API_KEY),
        "timestamp": datetime.now().isoformat()
    }
    
    return health_status


def health_check() -> bool:
    """
    Perform comprehensive health check
    
    Returns:
        True if all critical services are healthy
    """
    health = check_health()
    
    # Critical services
    critical_services = ["telegram", "gemini"]
    all_healthy = all(health.get(service, False) for service in critical_services)
    
    if not all_healthy:
        missing = [s for s in critical_services if not health.get(s, False)]
        logger.warning(f"Health check failed: Missing services: {missing}")
    
    return all_healthy


def send_health_report() -> bool:
    """
    Send health report to Telegram
    
    Returns:
        True if report sent successfully
    """
    health = check_health()
    
    message = "🏥 시스템 헬스체크\n\n"
    
    for service, status in health.items():
        if service == "timestamp":
            continue
        emoji = "✅" if status else "❌"
        message += f"{emoji} {service.capitalize()}: {'정상' if status else '비정상'}\n"
    
    message += f"\n⏰ {health.get('timestamp', 'N/A')}"
    
    try:
        return send_message_sync(message)
    except Exception as e:
        logger.error(f"Failed to send health report: {e}")
        return False


def monitor_execution_time(func):
    """
    Decorator to monitor function execution time
    
    Args:
        func: Function to monitor
    
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} executed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    
    return wrapper

