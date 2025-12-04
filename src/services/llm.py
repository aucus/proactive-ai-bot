"""LLM service using Gemini"""

import logging
import google.generativeai as genai
from src.utils.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


def generate_text(prompt: str, model: str = "gemini-2.0-flash") -> str:
    """
    Generate text using Gemini
    
    Args:
        prompt: Input prompt
        model: Model name (default: gemini-2.0-flash)
    
    Returns:
        Generated text
    """
    try:
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Failed to generate text: {e}")
        return ""


def generate_weather_message(weather_data: dict) -> str:
    """
    Generate natural weather message using LLM
    
    Args:
        weather_data: Weather data dictionary
    
    Returns:
        Natural language weather message
    """
    prompt = f"""다음 날씨 정보를 바탕으로 친근하고 자연스러운 아침 인사 메시지를 작성해주세요.
한국어로 작성하고, 이모지를 적절히 사용해주세요.

날씨 정보:
- 현재 기온: {weather_data.get('temp', 'N/A')}°C
- 체감 온도: {weather_data.get('feels_like', 'N/A')}°C
- 최고/최저: {weather_data.get('temp_max', 'N/A')}°C / {weather_data.get('temp_min', 'N/A')}°C
- 강수확률: {weather_data.get('rain_probability', 0)}%
- 날씨 설명: {weather_data.get('description', '')}

옷차림 추천과 우산 필요 여부도 포함해주세요."""
    
    try:
        message = generate_text(prompt)
        return message if message else ""
    except Exception as e:
        logger.error(f"Failed to generate weather message: {e}")
        return ""


def summarize_news(news_text: str) -> str:
    """
    Summarize news article
    
    Args:
        news_text: News article text
    
    Returns:
        Summary text
    """
    prompt = f"""다음 뉴스 기사를 간결하게 2-3문장으로 요약해주세요.
핵심 내용만 포함하고, 한국어로 작성해주세요.

{news_text}"""
    
    try:
        summary = generate_text(prompt)
        return summary if summary else ""
    except Exception as e:
        logger.error(f"Failed to summarize news: {e}")
        return ""



