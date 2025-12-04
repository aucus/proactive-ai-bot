"""News service using News API and Google News RSS"""

import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from src.utils.config import NEWS_API_KEY
from src.services.llm import summarize_news

logger = logging.getLogger(__name__)

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
        # Get news from last 24 hours
        from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        params = {
            "q": query,
            "apiKey": NEWS_API_KEY,
            "language": "ko",
            "sortBy": "publishedAt",
            "from": from_date,
            "pageSize": max_results
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
    
    Args:
        topic: News topic (ai, tech, edtech)
        max_results: Maximum number of results
    
    Returns:
        List of news items
    """
    try:
        import feedparser
        
        rss_url = GOOGLE_NEWS_RSS.get(topic, GOOGLE_NEWS_RSS["ai"])
        feed = feedparser.parse(rss_url)
        
        news_items = []
        for entry in feed.entries[:max_results]:
            news_items.append({
                "title": entry.get("title", ""),
                "description": entry.get("summary", ""),
                "url": entry.get("link", ""),
                "source": "Google News",
                "published_at": entry.get("published", ""),
                "category": _categorize_news(entry.get("title", ""), entry.get("summary", ""))
            })
        
        logger.info(f"Retrieved {len(news_items)} news articles from RSS")
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


def get_news_briefing(max_items: int = 5) -> List[Dict]:
    """
    Get news briefing from multiple sources
    
    Args:
        max_items: Maximum number of news items
    
    Returns:
        List of news items with summaries
    """
    all_news = []
    
    # Try News API first
    if NEWS_API_KEY:
        for topic in ["AI", "technology", "edtech"]:
            news = get_news_from_api(topic, max_results=3)
            all_news.extend(news)
            if len(all_news) >= max_items:
                break
    
    # Fallback to RSS if API fails or not configured
    if not all_news:
        logger.info("Using RSS fallback for news")
        for topic in ["ai", "tech", "edtech"]:
            news = get_news_from_rss(topic, max_results=2)
            all_news.extend(news)
            if len(all_news) >= max_items:
                break
    
    # Remove duplicates (by title)
    seen_titles = set()
    unique_news = []
    for item in all_news:
        title = item.get("title", "").lower()
        if title not in seen_titles and len(title) > 10:
            seen_titles.add(title)
            unique_news.append(item)
            if len(unique_news) >= max_items:
                break
    
    # Generate summaries using LLM
    for item in unique_news:
        if not item.get("summary"):
            description = item.get("description", "")
            if description:
                summary = summarize_news(description[:500])  # Limit length
                item["summary"] = summary if summary else description[:150] + "..."
            else:
                item["summary"] = item.get("title", "")
    
    logger.info(f"Generated news briefing with {len(unique_news)} items")
    return unique_news[:max_items]

