"""User settings management using GitHub Gist"""

import logging
import json
from typing import Dict, Optional, Any
from src.utils.storage import save_state, load_state

logger = logging.getLogger(__name__)

# Default settings
DEFAULT_SETTINGS = {
    "notifications": {
        "weather": True,
        "news": True,
        "schedule": True,
        "evening": True,
        "night": True
    },
    "news_categories": ["AI", "Tech", "EdTech"],
    "location": {
        "city": "Seoul",
        "country_code": "KR"
    },
    "notification_times": {
        "weather": "07:00",
        "news": "08:00",
        "schedule": "09:30",
        "evening": "18:00",
        "night": "21:00"
    }
}

# Settings Gist ID (should be stored in environment or first run creates it)
SETTINGS_GIST_ID_KEY = "SETTINGS_GIST_ID"


def get_settings_gist_id() -> Optional[str]:
    """Get settings Gist ID from environment"""
    import os
    return os.getenv(SETTINGS_GIST_ID_KEY, "")


def set_settings_gist_id(gist_id: str):
    """Set settings Gist ID (for first run)"""
    import os
    # Note: This doesn't persist across runs in GitHub Actions
    # Should be stored in a separate Gist or environment variable
    os.environ[SETTINGS_GIST_ID_KEY] = gist_id


def load_settings(gist_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Load user settings from Gist
    
    Args:
        gist_id: Gist ID (if None, tries to get from environment)
    
    Returns:
        Settings dictionary
    """
    if not gist_id:
        gist_id = get_settings_gist_id()
    
    if not gist_id:
        logger.info("No settings Gist ID found, using defaults")
        return DEFAULT_SETTINGS.copy()
    
    settings = load_state(gist_id, "settings.json")
    if settings:
        # Merge with defaults to ensure all keys exist
        merged = DEFAULT_SETTINGS.copy()
        merged.update(settings)
        return merged
    
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict[str, Any], gist_id: Optional[str] = None) -> Optional[str]:
    """
    Save user settings to Gist
    
    Args:
        settings: Settings dictionary
        gist_id: Existing Gist ID (if None, creates new)
    
    Returns:
        Gist ID or None
    """
    saved_gist_id = save_state(settings, gist_id, "settings.json")
    
    if saved_gist_id and not gist_id:
        # First time save, store the Gist ID
        set_settings_gist_id(saved_gist_id)
        logger.info(f"Created new settings Gist: {saved_gist_id}")
    
    return saved_gist_id


def update_setting(key: str, value: Any, gist_id: Optional[str] = None) -> bool:
    """
    Update a single setting
    
    Args:
        key: Setting key (supports dot notation, e.g., "notifications.weather")
        value: New value
        gist_id: Gist ID
    
    Returns:
        True if successful
    """
    settings = load_settings(gist_id)
    
    # Handle dot notation
    keys = key.split(".")
    current = settings
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    current[keys[-1]] = value
    
    saved_id = save_settings(settings, gist_id)
    return saved_id is not None


def get_setting(key: str, default: Any = None, gist_id: Optional[str] = None) -> Any:
    """
    Get a single setting value
    
    Args:
        key: Setting key (supports dot notation)
        default: Default value if not found
        gist_id: Gist ID
    
    Returns:
        Setting value or default
    """
    settings = load_settings(gist_id)
    
    # Handle dot notation
    keys = key.split(".")
    current = settings
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    
    return current


def is_notification_enabled(notification_type: str, gist_id: Optional[str] = None) -> bool:
    """
    Check if a notification type is enabled
    
    Args:
        notification_type: Type of notification (weather, news, schedule, etc.)
        gist_id: Gist ID
    
    Returns:
        True if enabled
    """
    return get_setting(f"notifications.{notification_type}", True, gist_id)

