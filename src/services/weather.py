"""Weather service using OpenWeatherMap API"""

import logging
import requests
from typing import Dict, Optional
from src.utils.config import OPENWEATHER_API_KEY

logger = logging.getLogger(__name__)

# OpenWeatherMap API endpoint
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_API_URL = "https://api.openweathermap.org/data/2.5/forecast"


def get_weather_from_web(city: str = "Seoul", country_code: str = "KR") -> Optional[Dict]:
    """
    Get weather data from web (fallback when API key is not available)
    Uses wttr.in service (no API key required)
    
    Args:
        city: City name (default: Seoul)
        country_code: Country code (default: KR)
    
    Returns:
        Weather data dictionary or None
    """
    try:
        # wttr.in provides weather data without API key
        # Format: wttr.in/{city}?format=j1 (JSON format)
        url = f"https://wttr.in/{city}?format=j1"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WeatherBot/1.0)"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse wttr.in JSON format
        current = data.get("current_condition", [{}])[0]
        temp_c = float(current.get("temp_C", 0))
        feels_like_c = float(current.get("FeelsLikeC", temp_c))
        description = current.get("weatherDesc", [{}])[0].get("value", "알 수 없음")
        humidity = int(current.get("humidity", 0))
        
        # Get today's forecast for min/max
        today = data.get("weather", [{}])[0]
        temp_max = float(today.get("maxtempC", temp_c))
        temp_min = float(today.get("mintempC", temp_c))
        
        # Estimate rain probability from description
        desc_lower = description.lower()
        rain_probability = 0
        if any(word in desc_lower for word in ["rain", "비", "shower", "drizzle", "소나기"]):
            rain_probability = 60
        elif any(word in desc_lower for word in ["cloud", "구름", "overcast"]):
            rain_probability = 30
        
        weather_data = {
            "temp": round(temp_c),
            "feels_like": round(feels_like_c),
            "temp_min": round(temp_min),
            "temp_max": round(temp_max),
            "humidity": humidity,
            "description": description,
            "rain_probability": rain_probability,
            "wind_speed": float(current.get("windspeedKmph", 0)) / 3.6,  # km/h to m/s
            "city": city
        }
        
        logger.info(f"Weather data retrieved from web for {city}")
        return weather_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get weather from web: {e}")
        return None
    except (KeyError, ValueError, IndexError) as e:
        logger.error(f"Failed to parse weather data from web: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting weather from web: {e}")
        return None


def get_weather(city: str = "Seoul", country_code: str = "KR") -> Optional[Dict]:
    """
    Get current weather data
    Tries OpenWeatherMap API first, falls back to web scraping if API key is not available
    
    Args:
        city: City name (default: Seoul)
        country_code: Country code (default: KR)
    
    Returns:
        Weather data dictionary or None
    """
    # Try OpenWeatherMap API first if key is available
    if OPENWEATHER_API_KEY:
        try:
            params = {
                "q": f"{city},{country_code}",
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "kr"
            }
            
            response = requests.get(WEATHER_API_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant data
            weather_data = {
                "temp": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "temp_min": round(data["main"]["temp_min"]),
                "temp_max": round(data["main"]["temp_max"]),
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "rain_probability": _get_rain_probability(data),
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "city": data["name"]
            }
            
            logger.info(f"Weather data retrieved from OpenWeatherMap for {city}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"OpenWeatherMap API failed: {e}, trying web fallback...")
        except (KeyError, ValueError) as e:
            logger.warning(f"OpenWeatherMap API response error: {e}, trying web fallback...")
        except Exception as e:
            logger.warning(f"OpenWeatherMap API unexpected error: {e}, trying web fallback...")
    
    # Fallback to web scraping
    logger.info("Using web fallback for weather data")
    return get_weather_from_web(city, country_code)
    
    try:
        params = {
            "q": f"{city},{country_code}",
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "kr"
        }
        
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant data
        weather_data = {
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "temp_min": round(data["main"]["temp_min"]),
            "temp_max": round(data["main"]["temp_max"]),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "rain_probability": _get_rain_probability(data),
            "wind_speed": data.get("wind", {}).get("speed", 0),
            "city": data["name"]
        }
        
        logger.info(f"Weather data retrieved for {city}")
        return weather_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get weather data: {e}")
        return None
    except KeyError as e:
        logger.error(f"Unexpected API response format: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def _get_rain_probability(data: Dict) -> int:
    """Extract rain probability from API response"""
    # OpenWeatherMap current weather doesn't provide probability
    # Check if rain exists in response
    if "rain" in data:
        return 50  # Estimate if rain is present
    return 0


def get_forecast(city: str = "Seoul", country_code: str = "KR") -> Optional[Dict]:
    """
    Get weather forecast
    
    Args:
        city: City name (default: Seoul)
        country_code: Country code (default: KR)
    
    Returns:
        Forecast data dictionary or None
    """
    if not OPENWEATHER_API_KEY:
        logger.warning("OpenWeatherMap API key not set")
        return None
    
    try:
        params = {
            "q": f"{city},{country_code}",
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "kr",
            "cnt": 5  # 5 forecasts (every 3 hours)
        }
        
        response = requests.get(FORECAST_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get forecast: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None



