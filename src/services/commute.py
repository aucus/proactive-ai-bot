"""Commute weather service - home and office weather"""

import logging
from typing import Dict, Optional
from src.services.weather import get_weather
from src.utils.user_config import get_location

logger = logging.getLogger(__name__)


def get_commute_weather() -> Dict[str, Optional[Dict]]:
    """
    Get weather for both home and office locations
    
    Returns:
        Dictionary with 'home' and 'office' weather data
    """
    home_location = get_location("home")
    office_location = get_location("office")
    
    home_weather = get_weather(
        city=home_location["city"],
        country_code=home_location["country_code"]
    )
    
    office_weather = get_weather(
        city=office_location["city"],
        country_code=office_location["country_code"]
    )
    
    return {
        "home": home_weather,
        "office": office_weather,
        "home_location": home_location,
        "office_location": office_location
    }

