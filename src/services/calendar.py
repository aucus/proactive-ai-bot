"""Google Calendar service"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.utils.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN

logger = logging.getLogger(__name__)

# Google Calendar API
CALENDAR_API_URL = "https://www.googleapis.com/calendar/v3"


def _get_access_token() -> Optional[str]:
    """
    Get access token using refresh token
    
    Returns:
        Access token or None
    """
    if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN]):
        logger.warning("Google OAuth credentials not configured")
        return None
    
    try:
        import requests
        
        url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": GOOGLE_REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data.get("access_token")
        
    except Exception as e:
        logger.error(f"Failed to get access token: {e}")
        return None


def get_today_events(calendar_id: str = "primary") -> List[Dict]:
    """
    Get today's calendar events
    
    Args:
        calendar_id: Calendar ID (default: primary)
    
    Returns:
        List of event dictionaries
    """
    access_token = _get_access_token()
    if not access_token:
        logger.warning("Cannot get calendar events: OAuth not configured")
        return []
    
    try:
        import requests
        
        # Get today's date range
        now = datetime.now()
        time_min = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
        time_max = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
        
        url = f"{CALENDAR_API_URL}/calendars/{calendar_id}/events"
        params = {
            "timeMin": time_min,
            "timeMax": time_max,
            "singleEvents": True,
            "orderBy": "startTime",
            "maxResults": 20
        }
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        events = data.get("items", [])
        
        formatted_events = []
        for event in events:
            start = event.get("start", {})
            end = event.get("end", {})
            
            # Parse datetime
            start_time = start.get("dateTime") or start.get("date")
            end_time = end.get("dateTime") or end.get("date")
            
            # Format time for display
            if start_time:
                try:
                    if "T" in start_time:
                        dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                        time_str = dt.strftime("%H:%M")
                    else:
                        time_str = "하루 종일"
                except:
                    time_str = start_time
            else:
                time_str = "시간 미정"
            
            formatted_events.append({
                "title": event.get("summary", "제목 없음"),
                "time": time_str,
                "start": start_time,
                "end": end_time,
                "location": event.get("location", ""),
                "description": event.get("description", ""),
                "all_day": "date" in start,
                "important": _is_important_event(event)
            })
        
        logger.info(f"Retrieved {len(formatted_events)} events for today")
        return formatted_events
        
    except Exception as e:
        logger.error(f"Failed to get calendar events: {e}")
        return []


def get_tomorrow_events(calendar_id: str = "primary") -> List[Dict]:
    """
    Get tomorrow's calendar events
    
    Args:
        calendar_id: Calendar ID (default: primary)
    
    Returns:
        List of event dictionaries
    """
    access_token = _get_access_token()
    if not access_token:
        logger.warning("Cannot get calendar events: OAuth not configured")
        return []
    
    try:
        import requests
        
        # Get tomorrow's date range
        tomorrow = datetime.now() + timedelta(days=1)
        time_min = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
        time_max = (tomorrow + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
        
        url = f"{CALENDAR_API_URL}/calendars/{calendar_id}/events"
        params = {
            "timeMin": time_min,
            "timeMax": time_max,
            "singleEvents": True,
            "orderBy": "startTime",
            "maxResults": 20
        }
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        events = data.get("items", [])
        
        formatted_events = []
        for event in events:
            start = event.get("start", {})
            end = event.get("end", {})
            
            start_time = start.get("dateTime") or start.get("date")
            end_time = end.get("dateTime") or end.get("date")
            
            if start_time:
                try:
                    if "T" in start_time:
                        dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                        time_str = dt.strftime("%H:%M")
                    else:
                        time_str = "하루 종일"
                except:
                    time_str = start_time
            else:
                time_str = "시간 미정"
            
            formatted_events.append({
                "title": event.get("summary", "제목 없음"),
                "time": time_str,
                "start": start_time,
                "end": end_time,
                "location": event.get("location", ""),
                "description": event.get("description", ""),
                "all_day": "date" in start,
                "important": _is_important_event(event)
            })
        
        logger.info(f"Retrieved {len(formatted_events)} events for tomorrow")
        return formatted_events
        
    except Exception as e:
        logger.error(f"Failed to get calendar events: {e}")
        return []


def _is_important_event(event: Dict) -> bool:
    """
    Determine if event is important based on keywords
    
    Args:
        event: Event dictionary
    
    Returns:
        True if important
    """
    title = event.get("summary", "").lower()
    description = event.get("description", "").lower()
    text = title + " " + description
    
    important_keywords = [
        "회의", "미팅", "meeting", "conference",
        "데드라인", "deadline", "due",
        "프레젠테이션", "presentation",
        "리뷰", "review"
    ]
    
    return any(keyword in text for keyword in important_keywords)


def get_schedule_briefing() -> Dict:
    """
    Get schedule briefing for today
    
    Returns:
        Dictionary with today's events
    """
    today_events = get_today_events()
    
    # Filter events for today (remove past events)
    now = datetime.now()
    upcoming_events = []
    
    for event in today_events:
        start = event.get("start", "")
        if start:
            try:
                if "T" in start:
                    event_time = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    # Only include future events or events within last hour
                    if event_time >= now - timedelta(hours=1):
                        upcoming_events.append(event)
                else:
                    # All-day event
                    upcoming_events.append(event)
            except:
                # If parsing fails, include it
                upcoming_events.append(event)
        else:
            upcoming_events.append(event)
    
    return {
        "events": upcoming_events,
        "count": len(upcoming_events),
        "important_count": sum(1 for e in upcoming_events if e.get("important", False))
    }

