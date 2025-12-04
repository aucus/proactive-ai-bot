"""Configuration management"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_env(key: str, default: str = None) -> str:
    """Get environment variable"""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set")
    return value


# Telegram (required, but allow empty for testing)
try:
    TELEGRAM_TOKEN = get_env("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = get_env("TELEGRAM_CHAT_ID")
except ValueError:
    TELEGRAM_TOKEN = ""
    TELEGRAM_CHAT_ID = ""

# LLM (required, but allow empty for testing)
try:
    GEMINI_API_KEY = get_env("GEMINI_API_KEY")
except ValueError:
    GEMINI_API_KEY = ""

# Weather
OPENWEATHER_API_KEY = get_env("OPENWEATHER_API_KEY", "")

# Google APIs (Phase 2)
GOOGLE_CLIENT_ID = get_env("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = get_env("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN = get_env("GOOGLE_REFRESH_TOKEN", "")

# Optional
NEWS_API_KEY = get_env("NEWS_API_KEY", "")
YOUTUBE_API_KEY = get_env("YOUTUBE_API_KEY", "")
GIST_TOKEN = get_env("GIST_TOKEN", "")

# Qdrant/Obsidian (Optional)
QDRANT_URL = get_env("QDRANT_URL", "")
QDRANT_API_KEY = get_env("QDRANT_API_KEY", "")
OBSIDIAN_VAULT_PATH = get_env("OBSIDIAN_VAULT_PATH", "")



