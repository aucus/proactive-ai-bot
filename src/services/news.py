"""News service using News API and Google News RSS"""

import logging
import requests
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from src.utils.config import NEWS_API_KEY, GIST_TOKEN
from src.services.llm import summarize_news
from src.utils.storage import load_state, save_state

logger = logging.getLogger(__name__)

KST = ZoneInfo("Asia/Seoul")

# News state Gist ID (can be set via environment variable)
NEWS_GIST_ID_KEY = "NEWS_GIST_ID"


def get_news_gist_id() -> Optional[str]:
    """Get news state Gist ID from environment"""
    import os
    gist_id = os.getenv(NEWS_GIST_ID_KEY, "")
    if not gist_id:
        # Fallback to SETTINGS_GIST_ID if available
        gist_id = os.getenv("SETTINGS_GIST_ID", "")
    return gist_id if gist_id else None

# News API endpoint
NEWS_API_URL = "https://newsapi.org/v2/everything"

# Google News RSS feeds (backup)
GOOGLE_NEWS_RSS = {
    "ai": "https://news.google.com/rss/search?q=artificial+intelligence+machine+learning&hl=ko&gl=KR&ceid=KR:ko",
    "tech": "https://news.google.com/rss/search?q=technology+tech+industry&hl=ko&gl=KR&ceid=KR:ko",
    "edtech": "https://news.google.com/rss/search?q=edtech+education+technology&hl=ko&gl=KR&ceid=KR:ko"
}

# 관심사 키워드
INTEREST_TOPICS = {
    "ai": ["AI", "artificial intelligence", "machine learning", "deep learning", "LLM", "GPT", "Claude"],
    "tech": ["technology", "tech", "startup", "innovation", "software", "hardware"],
    "edtech": ["edtech", "education technology", "online learning", "e-learning", "교육"]
}


def get_news_from_api(query: str, max_results: int = 5) -> List[Dict]:
    """
    Get news from News API
    
    Args:
        query: Search query
        max_results: Maximum number of results
    
    Returns:
        List of news items
    """
    if not NEWS_API_KEY:
        logger.warning("News API key not set, skipping API call")
        return []
    
    try:
        # Get news from last 12 hours to get fresher content
        now_kst = datetime.now(KST)
        from_time = now_kst - timedelta(hours=12)
        from_date = from_time.strftime("%Y-%m-%d")
        from_datetime = from_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        params = {
            "q": query,
            "apiKey": NEWS_API_KEY,
            "language": "ko",
            "sortBy": "publishedAt",
            "from": from_datetime,
            "pageSize": max_results * 2  # Get more to filter duplicates
        }
        
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("articles", [])
        
        news_items = []
        for article in articles[:max_results]:
            news_items.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "published_at": article.get("publishedAt", ""),
                "category": _categorize_news(article.get("title", ""), article.get("description", ""))
            })
        
        logger.info(f"Retrieved {len(news_items)} news articles from News API")
        return news_items
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get news from API: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting news: {e}")
        return []


def get_news_from_rss(topic: str = "ai", max_results: int = 5) -> List[Dict]:
    """
    Get news from Google News RSS (backup method)
    Only returns articles from last 12 hours
    
    Args:
        topic: News topic (ai, tech, edtech)
        max_results: Maximum number of results
    
    Returns:
        List of news items
    """
    try:
        import feedparser
        from email.utils import parsedate_to_datetime
        
        rss_url = GOOGLE_NEWS_RSS.get(topic, GOOGLE_NEWS_RSS["ai"])
        feed = feedparser.parse(rss_url)
        
        now_kst = datetime.now(KST)
        cutoff_time = now_kst - timedelta(hours=12)
        
        news_items = []
        for entry in feed.entries:
            try:
                # Parse published time
                published_str = entry.get("published", "")
                if published_str:
                    published_dt = parsedate_to_datetime(published_str)
                    # Convert to KST if timezone-aware, otherwise assume KST
                    if published_dt.tzinfo is None:
                        published_dt = published_dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(KST)
                    else:
                        published_dt = published_dt.astimezone(KST)
                    
                    # Only include recent articles (last 12 hours)
                    if published_dt < cutoff_time:
                        continue
                
                news_items.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "source": "Google News",
                    "published_at": published_str,
                    "category": _categorize_news(entry.get("title", ""), entry.get("summary", ""))
                })
                
                if len(news_items) >= max_results * 2:  # Get more to filter duplicates
                    break
            except Exception as e:
                logger.warning(f"Failed to parse RSS entry: {e}")
                continue
        
        logger.info(f"Retrieved {len(news_items)} recent news articles from RSS")
        return news_items
        
    except ImportError:
        logger.warning("feedparser not installed, RSS fallback unavailable")
        return []
    except Exception as e:
        logger.error(f"Failed to get news from RSS: {e}")
        return []


def _categorize_news(title: str, description: str) -> str:
    """
    Categorize news based on keywords
    
    Args:
        title: News title
        description: News description
    
    Returns:
        Category name (AI, Tech, EdTech, News)
    """
    text = (title + " " + description).lower()
    
    # Check AI keywords
    if any(keyword.lower() in text for keyword in INTEREST_TOPICS["ai"]):
        return "AI"
    
    # Check EdTech keywords
    if any(keyword.lower() in text for keyword in INTEREST_TOPICS["edtech"]):
        return "EdTech"
    
    # Check Tech keywords
    if any(keyword.lower() in text for keyword in INTEREST_TOPICS["tech"]):
        return "Tech"
    
    return "News"


def _get_seen_news_urls(gist_id: Optional[str] = None) -> Set[str]:
    """
    Get set of already seen news URLs from Gist
    
    Args:
        gist_id: Optional Gist ID for state storage
    
    Returns:
        Set of seen URLs
    """
    if not GIST_TOKEN or not gist_id:
        return set()
    
    try:
        state = load_state(gist_id, "news_state.json")
        if state:
            seen_urls_list = state.get("seen_urls", [])
            # Keep only URLs from last 7 days to prevent unbounded growth
            cutoff_date = (datetime.now(KST) - timedelta(days=7)).isoformat()
            # Filter by date and extract URLs
            filtered_urls = [url for url, date in seen_urls_list if date >= cutoff_date]
            return set(filtered_urls)
    except Exception as e:
        logger.warning(f"Failed to load seen news URLs: {e}")
    
    return set()


def _save_seen_news_urls(urls: Set[str], gist_id: Optional[str] = None) -> Optional[str]:
    """
    Save seen news URLs to Gist
    Merges with existing URLs to preserve history
    
    Args:
        urls: Set of new URLs to save
        gist_id: Optional Gist ID for state storage
    
    Returns:
        Gist ID if successful
    """
    if not GIST_TOKEN:
        return None
    
    try:
        now = datetime.now(KST).isoformat()
        cutoff_date = (datetime.now(KST) - timedelta(days=7)).isoformat()
        
        # Load existing URLs
        existing_urls = _get_seen_news_urls(gist_id)
        
        # Merge with new URLs
        all_urls = existing_urls | urls
        
        # Convert to list of tuples with current timestamp
        seen_urls_list = [(url, now) for url in all_urls]
        
        state = {
            "seen_urls": seen_urls_list,
            "last_updated": now
        }
        
        if gist_id:
            return save_state(state, gist_id, "news_state.json")
        else:
            new_gist_id = save_state(state, None, "news_state.json")
            return new_gist_id
    except Exception as e:
        logger.warning(f"Failed to save seen news URLs: {e}")
        return None


def get_news_briefing(max_items: int = 5, gist_id: Optional[str] = None) -> List[Dict]:
    """
    Get news briefing from multiple sources
    Filters out already seen news articles
    
    Args:
        max_items: Maximum number of news items
        gist_id: Optional Gist ID for tracking seen news (if None, tries to get from env)
    
    Returns:
        List of news items with summaries
    """
    # Get Gist ID if not provided
    if not gist_id:
        gist_id = get_news_gist_id()
    
    # Load seen URLs
    seen_urls = _get_seen_news_urls(gist_id)
    logger.info(f"Loaded {len(seen_urls)} seen news URLs")
    
    all_news = []
    
    # Try News API first
    if NEWS_API_KEY:
        for topic in ["AI", "technology", "edtech"]:
            news = get_news_from_api(topic, max_results=5)
            all_news.extend(news)
            if len(all_news) >= max_items * 2:
                break
    
    # Fallback to RSS if API fails or not configured
    if not all_news:
        logger.info("Using RSS fallback for news")
        for topic in ["ai", "tech", "edtech"]:
            news = get_news_from_rss(topic, max_results=3)
            all_news.extend(news)
            if len(all_news) >= max_items * 2:
                break
    
    # Remove duplicates by URL and title, and filter seen URLs
    seen_titles = set()
    unique_news = []
    new_urls = set()
    
    for item in all_news:
        url = item.get("url", "")
        title = item.get("title", "").lower().strip()
        
        # Skip if already seen or duplicate
        if url in seen_urls:
            logger.debug(f"Skipping seen URL: {url[:50]}...")
            continue
        
        if not url or len(title) < 10:
            continue
        
        # Check for duplicate titles
        if title in seen_titles:
            continue
        
        seen_titles.add(title)
        unique_news.append(item)
        new_urls.add(url)
        
        if len(unique_news) >= max_items:
            break
    
    # Generate concise summaries using LLM (limit to 50 chars)
    for item in unique_news:
        if not item.get("summary"):
            description = item.get("description", "")
            if description:
                # Generate short summary (one line, ~50 chars)
                summary = summarize_news(description[:300])
                if summary:
                    # Limit to 50 characters for concise display
                    summary = summary.strip()
                    if len(summary) > 50:
                        summary = summary[:47] + "..."
                    item["summary"] = summary
                else:
                    # Fallback: use description truncated
                    item["summary"] = description[:50] + "..." if len(description) > 50 else description
            else:
                item["summary"] = ""
    
    # Save new URLs to Gist
    if new_urls and GIST_TOKEN:
        updated_seen_urls = seen_urls | new_urls
        _save_seen_news_urls(updated_seen_urls, gist_id)
        logger.info(f"Saved {len(new_urls)} new URLs to seen list")
    
    logger.info(f"Generated news briefing with {len(unique_news)} new items")
    return unique_news[:max_items]


