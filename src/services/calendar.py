"""Google Calendar service"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from zoneinfo import ZoneInfo
from src.utils.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN

logger = logging.getLogger(__name__)

# Timezone 설정 (한국 시간)
KST = ZoneInfo("Asia/Seoul")
UTC = ZoneInfo("UTC")

# Google Calendar API
CALENDAR_API_URL = "https://www.googleapis.com/calendar/v3"


def is_calendar_configured() -> bool:
    """Return True if OAuth env vars are configured (non-empty)."""
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_REFRESH_TOKEN)


def _get_access_token() -> Optional[str]:
    """
    Get access token using refresh token
    
    Returns:
        Access token or None
    """
    if not is_calendar_configured():
        logger.warning(
            "Google OAuth credentials not configured "
            f"(GOOGLE_CLIENT_ID={bool(GOOGLE_CLIENT_ID)}, "
            f"GOOGLE_CLIENT_SECRET={bool(GOOGLE_CLIENT_SECRET)}, "
            f"GOOGLE_REFRESH_TOKEN={bool(GOOGLE_REFRESH_TOKEN)})"
        )
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
    Uses KST timezone to ensure consistent behavior in GitHub Actions (UTC) and local environments
    
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
        
        # Get today's date range in KST (한국 시간 기준)
        # GitHub Actions는 UTC를 사용하므로 명시적으로 KST로 변환
        now_utc = datetime.now(UTC)
        now_kst = now_utc.astimezone(KST)
        today_kst = now_kst.date()
        
        # KST 기준 오늘 00:00과 내일 00:00을 UTC로 변환하여 API 호출
        today_start_kst = datetime.combine(today_kst, datetime.min.time()).replace(tzinfo=KST)
        today_end_kst = datetime.combine(today_kst + timedelta(days=1), datetime.min.time()).replace(tzinfo=KST)
        
        time_min = today_start_kst.astimezone(UTC).isoformat().replace('+00:00', 'Z')
        time_max = today_end_kst.astimezone(UTC).isoformat().replace('+00:00', 'Z')
        
        logger.info(f"Fetching events for {today_kst} (KST) - from {time_min} to {time_max} (UTC)")
        
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
        
        if len(formatted_events) == 0:
            logger.warning(f"No events found for {today_kst} (KST). API returned {len(events)} raw events.")
            if len(events) > 0:
                logger.debug(f"Raw events: {events[:2]}")  # Log first 2 events for debugging
        
        return formatted_events
        
    except Exception as e:
        logger.error(f"Failed to get calendar events: {e}", exc_info=True)
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
    Uses KST timezone to ensure consistent behavior in GitHub Actions (UTC) and local environments
    
    Returns:
        Dictionary with today's events
    """
    today_events = get_today_events()
    
    # Get current time in KST (한국 시간)
    # GitHub Actions는 UTC를 사용하므로 명시적으로 KST로 변환
    now_utc = datetime.now(UTC)
    now_kst = now_utc.astimezone(KST)
    today_kst = now_kst.date()
    
    logger.info(f"Current time (KST): {now_kst.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Today (KST): {today_kst}")
    logger.info(f"Total events retrieved: {len(today_events)}")
    
    upcoming_events = []
    
    for event in today_events:
        start = event.get("start", "")
        if start:
            try:
                if "T" in start:
                    # Parse event time and convert to KST
                    try:
                        if start.endswith("Z"):
                            # UTC time
                            event_time_utc = datetime.fromisoformat(start.replace("Z", "+00:00")).replace(tzinfo=UTC)
                            event_time = event_time_utc.astimezone(KST)
                        elif "+" in start or "-" in start[-6:]:  # Has timezone offset like +09:00 or -05:00
                            # Has timezone info (e.g., 2025-12-05T15:00:00+09:00)
                            event_time = datetime.fromisoformat(start)
                            if event_time.tzinfo is None:
                                # Should not happen, but assume KST if no timezone
                                logger.warning(f"Event time has no timezone info: {start}, assuming KST")
                                event_time = event_time.replace(tzinfo=KST)
                            else:
                                event_time = event_time.astimezone(KST)
                        else:
                            # No timezone, assume KST
                            event_time = datetime.fromisoformat(start).replace(tzinfo=KST)
                        
                        # Check if event is today (KST) and not too far in the past
                        event_date = event_time.date()
                        time_diff = (event_time - now_kst).total_seconds() / 3600  # hours
                        
                        # Include events that are:
                        # 1. Today (KST)
                        # 2. Not more than 1 hour in the past
                        if event_date == today_kst and time_diff >= -1:
                            upcoming_events.append(event)
                            logger.info(f"Included event: {event.get('title')} at {event_time.strftime('%Y-%m-%d %H:%M')} KST (diff: {time_diff:.1f}h)")
                        else:
                            logger.warning(f"Excluded event: {event.get('title')} - date: {event_date} (expected: {today_kst}), time_diff: {time_diff:.1f}h")
                    except Exception as parse_error:
                        logger.error(f"Failed to parse event time '{start}': {parse_error}, including event anyway")
                        upcoming_events.append(event)
                else:
                    # All-day event (date only, no time)
                    # Include all all-day events for today
                    event_date = datetime.fromisoformat(start).date()
                    if event_date == today_kst:
                        upcoming_events.append(event)
                        logger.debug(f"Included all-day event: {event.get('title')}")
            except Exception as e:
                # If parsing fails, include it to be safe
                logger.warning(f"Failed to parse event time '{start}': {e}, including event anyway")
                upcoming_events.append(event)
        else:
            # No start time, include it
            upcoming_events.append(event)
    
    logger.info(f"Filtered events count: {len(upcoming_events)}")
    
    if len(upcoming_events) == 0 and len(today_events) > 0:
        logger.warning(f"All {len(today_events)} events were filtered out. This might indicate a timezone or filtering issue.")
        # Log first event details for debugging
        if today_events:
            first_event = today_events[0]
            logger.warning(f"First event details: title={first_event.get('title')}, start={first_event.get('start')}, time={first_event.get('time')}")
    
    return {
        "events": upcoming_events,
        "count": len(upcoming_events),
        "important_count": sum(1 for e in upcoming_events if e.get("important", False))
    }


