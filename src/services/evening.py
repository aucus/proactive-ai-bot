"""Evening reminder service"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.services.calendar import get_today_events, get_tomorrow_events

logger = logging.getLogger(__name__)


def get_evening_schedule() -> Dict:
    """
    Get evening schedule (today evening and tomorrow morning)
    
    Returns:
        Dictionary with evening events and tomorrow preview
    """
    now = datetime.now()
    evening_start = now.replace(hour=18, minute=0, second=0, microsecond=0)
    
    # Get today's events
    today_events = get_today_events()
    
    # Filter evening events (after 18:00)
    evening_events = []
    for event in today_events:
        start = event.get("start", "")
        if start:
            try:
                if "T" in start:
                    event_time = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    if event_time >= evening_start:
                        evening_events.append(event)
                else:
                    # All-day event, include if it's today
                    evening_events.append(event)
            except:
                pass
    
    # Get tomorrow's important events
    tomorrow_events = get_tomorrow_events()
    tomorrow_important = [e for e in tomorrow_events if e.get("important", False)][:3]
    
    return {
        "evening_events": evening_events,
        "tomorrow_preview": tomorrow_important,
        "has_evening_plans": len(evening_events) > 0,
        "has_tomorrow_important": len(tomorrow_important) > 0
    }


def get_content_recommendations() -> List[Dict]:
    """
    Get content recommendations (simplified version)
    For now, return generic recommendations
    Can be enhanced with YouTube/TMDB API later
    
    Returns:
        List of content recommendations
    """
    # Placeholder recommendations
    # TODO: Integrate with YouTube Data API and TMDB API
    recommendations = [
        {
            "type": "article",
            "title": "오늘 읽을만한 기술 아티클",
            "description": "AI/ML 트렌드 관련 최신 글들을 추천해드려요",
            "source": "curated"
        },
        {
            "type": "video",
            "title": "인기 기술 유튜브 영상",
            "description": "요즘 핫한 개발/기술 관련 영상",
            "source": "youtube_trending"
        }
    ]
    
    logger.info("Content recommendations generated (placeholder)")
    return recommendations


def get_evening_briefing() -> Dict:
    """
    Get complete evening briefing
    
    Returns:
        Dictionary with all evening information
    """
    schedule = get_evening_schedule()
    recommendations = get_content_recommendations()
    
    return {
        "schedule": schedule,
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    }

