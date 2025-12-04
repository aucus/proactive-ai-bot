"""User configuration loader"""

import json
import logging
import os
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Default config path
CONFIG_PATH = Path(__file__).parent.parent.parent / "user_config.json"


def load_user_config() -> Dict[str, Any]:
    """
    Load user configuration from user_config.json
    
    Returns:
        Configuration dictionary
    """
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info("User config loaded successfully")
                return config
        else:
            logger.warning(f"User config not found at {CONFIG_PATH}, using defaults")
            return _get_default_config()
    except Exception as e:
        logger.error(f"Failed to load user config: {e}")
        return _get_default_config()


def _get_default_config() -> Dict[str, Any]:
    """Get default configuration"""
    return {
        "user": {
            "name": "사용자",
            "timezone": "Asia/Seoul"
        },
        "locations": {
            "home": {
                "city": "Seoul",
                "country_code": "KR",
                "display_name": "서울"
            },
            "office": {
                "city": "Seoul",
                "country_code": "KR",
                "display_name": "서울"
            }
        },
        "schedule": {
            "commute": {
                "departure_time": "06:30",
                "notification_time": "06:20",
                "enabled": True
            },
            "news": {
                "time": "08:00",
                "enabled": True
            },
            "work_schedule": {
                "time": "09:30",
                "enabled": True
            },
            "evening": {
                "time": "18:00",
                "enabled": True
            },
            "night_project": {
                "time": "21:00",
                "enabled": True
            }
        },
        "preferences": {
            "news_categories": ["AI", "Tech", "EdTech"],
            "language": "ko"
        }
    }


def get_location(location_type: str = "home") -> Dict[str, str]:
    """
    Get location configuration
    
    Args:
        location_type: "home" or "office"
    
    Returns:
        Location dictionary with city, country_code, display_name
    """
    config = load_user_config()
    locations = config.get("locations", {})
    return locations.get(location_type, {
        "city": "Seoul",
        "country_code": "KR",
        "display_name": "서울"
    })


def get_schedule_time(schedule_type: str) -> str:
    """
    Get schedule time for a specific type
    
    Args:
        schedule_type: "commute", "news", "work_schedule", "evening", "night_project"
    
    Returns:
        Time string in HH:MM format
    """
    config = load_user_config()
    schedule = config.get("schedule", {})
    schedule_info = schedule.get(schedule_type, {})
    
    if schedule_type == "commute":
        return schedule_info.get("notification_time", "06:20")
    else:
        return schedule_info.get("time", "08:00")


def is_schedule_enabled(schedule_type: str) -> bool:
    """
    Check if a schedule is enabled
    
    Args:
        schedule_type: Schedule type
    
    Returns:
        True if enabled
    """
    config = load_user_config()
    schedule = config.get("schedule", {})
    schedule_info = schedule.get(schedule_type, {})
    return schedule_info.get("enabled", True)

