"""News service using News API and Google News RSS"""

import logging
import requests
import re
import html as _html
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from src.utils.config import NEWS_API_KEY, GIST_TOKEN
from src.services.llm import summarize_news_headline
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


_TAG_RE = re.compile(r"<[^>]+>")


def _clean_text(text: str) -> str:
    """Best-effort cleanup for RSS/HTML-ish text."""
    if not text:
        return ""
    t = text.strip()
    # Unescape HTML entities
    try:
        t = _html.unescape(t)
    except Exception:
        pass
    # Remove HTML tags
    t = _TAG_RE.sub(" ", t)
    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


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
        logger.error(f"Failed to get news from API for query '{query}': {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}, body: {e.response.text[:200]}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting news for query '{query}': {e}", exc_info=True)
        return []


def get_news_from_rss(topic: str = "ai", max_results: int = 5, hours_limit: int = 24) -> List[Dict]:
    """
    Get news from Google News RSS (backup method)
    Returns articles from last N hours (default 24 hours)
    
    Args:
        topic: News topic (ai, tech, edtech)
        max_results: Maximum number of results
        hours_limit: Hours to look back (default 24, set to None to disable time limit)
    
    Returns:
        List of news items
    """
    try:
        import feedparser
        from email.utils import parsedate_to_datetime
        
        rss_url = GOOGLE_NEWS_RSS.get(topic, GOOGLE_NEWS_RSS["ai"])
        logger.info(f"Fetching RSS from: {rss_url}")
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.warning(f"No entries found in RSS feed for topic: {topic}")
            return []
        
        now_kst = datetime.now(KST)
        cutoff_time = now_kst - timedelta(hours=hours_limit) if hours_limit else None
        
        news_items = []
        skipped_old = 0
        for entry in feed.entries:
            try:
                # Parse published time
                published_str = entry.get("published", "")
                if published_str and cutoff_time:
                    try:
                        published_dt = parsedate_to_datetime(published_str)
                        # Convert to KST if timezone-aware, otherwise assume UTC
                        if published_dt.tzinfo is None:
                            published_dt = published_dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(KST)
                        else:
                            published_dt = published_dt.astimezone(KST)
                        
                        # Only include recent articles
                        if published_dt < cutoff_time:
                            skipped_old += 1
                            continue
                    except Exception as e:
                        logger.debug(f"Failed to parse date '{published_str}': {e}, including anyway")
                
                title = entry.get("title", "").strip()
                if not title or len(title) < 10:
                    continue
                
                news_items.append({
                    "title": title,
                    "description": entry.get("summary", "").strip(),
                    "url": entry.get("link", ""),
                    "source": "Google News",
                    "published_at": published_str,
                    "category": _categorize_news(title, entry.get("summary", ""))
                })
                
                if len(news_items) >= max_results * 2:  # Get more to filter duplicates
                    break
            except Exception as e:
                logger.warning(f"Failed to parse RSS entry: {e}")
                continue
        
        if skipped_old > 0:
            logger.info(f"Retrieved {len(news_items)} news articles from RSS (skipped {skipped_old} old articles)")
        else:
            logger.info(f"Retrieved {len(news_items)} news articles from RSS")
        return news_items
        
    except ImportError:
        logger.error("feedparser not installed, RSS fallback unavailable")
        return []
    except Exception as e:
        logger.error(f"Failed to get news from RSS for topic '{topic}': {e}", exc_info=True)
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
    api_success = False
    
    # Try News API first
    if NEWS_API_KEY:
        logger.info("Attempting to fetch news from News API...")
        for topic in ["AI", "technology", "edtech"]:
            try:
                news = get_news_from_api(topic, max_results=5)
                if news:
                    all_news.extend(news)
                    api_success = True
                    logger.info(f"Retrieved {len(news)} articles from News API for topic: {topic}")
                if len(all_news) >= max_items * 2:
                    break
            except Exception as e:
                logger.warning(f"Failed to get news from API for topic '{topic}': {e}")
    else:
        logger.info("News API key not configured, skipping API call")
    
    # Fallback to RSS if API fails or not configured
    if not all_news:
        logger.info("Using RSS fallback for news")
        # Try with 24-hour limit first
        for topic in ["ai", "tech", "edtech"]:
            news = get_news_from_rss(topic, max_results=5, hours_limit=24)
            if news:
                all_news.extend(news)
                logger.info(f"Retrieved {len(news)} articles from RSS for topic: {topic}")
            if len(all_news) >= max_items * 2:
                break
        
        # If still no news, try without time limit
        if not all_news:
            logger.info("No recent news found, trying without time limit...")
            for topic in ["ai", "tech", "edtech"]:
                news = get_news_from_rss(topic, max_results=5, hours_limit=None)
                if news:
                    all_news.extend(news)
                    logger.info(f"Retrieved {len(news)} articles from RSS (no time limit) for topic: {topic}")
                if len(all_news) >= max_items * 2:
                    break
    
    if not all_news:
        logger.error("Failed to retrieve any news from all sources")
        return []
    
    logger.info(f"Total news items retrieved: {len(all_news)}")
    
    # Remove duplicates by URL and title, and filter seen URLs
    seen_titles = set()
    unique_news = []
    new_urls = set()
    skipped_seen = 0
    
    for item in all_news:
        url = item.get("url", "")
        title = item.get("title", "").lower().strip()
        
        # Skip if already seen
        if url in seen_urls:
            skipped_seen += 1
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
    
    if skipped_seen > 0:
        logger.info(f"Filtered out {skipped_seen} already seen news items")
    
    if not unique_news:
        logger.warning("All news items were filtered out (already seen or duplicates)")
        # If all items were seen, return some anyway (user might want to see them again)
        if all_news:
            logger.info("Returning some news items despite being seen previously")
            for item in all_news[:max_items]:
                url = item.get("url", "")
                title = item.get("title", "").lower().strip()
                if url and len(title) >= 10:
                    if title not in seen_titles:
                        seen_titles.add(title)
                        unique_news.append(item)
                        if len(unique_news) >= max_items:
                            break
    
    # Create Korean one-line headlines (translate if needed)
    for item in unique_news:
        if item.get("headline"):
            continue

        raw_title = _clean_text(item.get("title", ""))
        raw_desc = _clean_text(item.get("description", ""))

        # Keep prompt payload small
        title_for_llm = raw_title[:200]
        desc_for_llm = raw_desc[:280]

        headline = summarize_news_headline(title_for_llm, desc_for_llm, max_chars=40)
        if headline:
            item["headline"] = headline
        else:
            # Fallback: use cleaned title
            item["headline"] = raw_title if raw_title else (raw_desc[:40] if raw_desc else "")
        # No need for longer summaries in telegram push; keep legacy field blank
        item["summary"] = item.get("summary", "")
    
    # Save new URLs to Gist
    if new_urls and GIST_TOKEN:
        try:
            updated_seen_urls = seen_urls | new_urls
            _save_seen_news_urls(updated_seen_urls, gist_id)
            logger.info(f"Saved {len(new_urls)} new URLs to seen list")
        except Exception as e:
            logger.warning(f"Failed to save seen URLs: {e}")
    
    logger.info(f"Generated news briefing with {len(unique_news)} new items")
    return unique_news[:max_items]


