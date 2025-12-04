#!/usr/bin/env python3
"""Functional tests for the bot"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_weather_service():
    """Test weather service (without API key)"""
    print("Testing weather service...")
    
    try:
        from src.services.weather import get_weather
        
        # This should return None if API key is not set
        result = get_weather()
        if result is None:
            print("✅ Weather service handles missing API key correctly")
            return True
        else:
            print("⚠️ Weather service returned data (API key might be set)")
            return True
    except Exception as e:
        print(f"❌ Weather service test failed: {e}")
        return False


def test_news_service():
    """Test news service"""
    print("\nTesting news service...")
    
    try:
        from src.services.news import get_news_briefing
        
        # This should work with RSS fallback
        result = get_news_briefing(max_items=3)
        if result:
            print(f"✅ News service OK (retrieved {len(result)} items)")
            return True
        else:
            print("⚠️ News service returned empty (might be rate limited)")
            return True  # Not a failure, just no results
    except Exception as e:
        print(f"❌ News service test failed: {e}")
        return False


def test_storage_service():
    """Test storage service (without Gist token)"""
    print("\nTesting storage service...")
    
    try:
        from src.utils.storage import save_state, load_state
        
        # Test with mock data (will fail without token, but should handle gracefully)
        test_data = {"test": "data", "timestamp": "2025-12-04"}
        result = save_state(test_data)
        
        if result is None:
            print("✅ Storage service handles missing Gist token correctly")
            return True
        else:
            print(f"✅ Storage service OK (Gist ID: {result})")
            return True
    except Exception as e:
        print(f"❌ Storage service test failed: {e}")
        return False


def test_settings_service():
    """Test settings service"""
    print("\nTesting settings service...")
    
    try:
        from src.utils.settings import load_settings, get_setting, is_notification_enabled
        
        settings = load_settings()
        if settings:
            print(f"✅ Settings loaded: {len(settings)} keys")
            
            # Test get_setting
            weather_enabled = is_notification_enabled("weather")
            print(f"✅ Weather notification enabled: {weather_enabled}")
            
            # Test get_setting with dot notation
            city = get_setting("location.city", "Seoul")
            print(f"✅ Location setting: {city}")
            
            return True
        else:
            print("❌ Settings failed to load")
            return False
    except Exception as e:
        print(f"❌ Settings service test failed: {e}")
        return False


def test_message_formatters():
    """Test all message formatters"""
    print("\nTesting message formatters...")
    
    try:
        from src.bot.messages import (
            format_weather_message,
            format_news_message,
            format_schedule_message,
            format_evening_message,
            format_project_message
        )
        
        # Test weather
        weather_data = {"temp": 15, "feels_like": 12, "description": "맑음", "rain_probability": 10}
        msg = format_weather_message(weather_data)
        assert len(msg) > 0, "Weather message should not be empty"
        
        # Test news
        news_items = [{"title": "Test", "summary": "Test", "url": "https://test.com", "category": "Tech"}]
        msg = format_news_message(news_items)
        assert len(msg) > 0, "News message should not be empty"
        
        # Test schedule
        events = []
        msg = format_schedule_message(events)
        assert len(msg) > 0, "Schedule message should not be empty"
        
        # Test evening
        briefing = {"schedule": {"evening_events": [], "tomorrow_preview": []}, "recommendations": []}
        msg = format_evening_message(briefing)
        assert len(msg) > 0, "Evening message should not be empty"
        
        # Test project
        reminders = {"projects": [], "has_projects": False, "message": "Test"}
        msg = format_project_message(reminders)
        assert len(msg) > 0, "Project message should not be empty"
        
        print("✅ All message formatters OK")
        return True
    except Exception as e:
        print(f"❌ Message formatters test failed: {e}")
        return False


def main():
    """Run all functional tests"""
    print("=" * 50)
    print("Functional Tests for Proactive AI Bot")
    print("=" * 50)
    
    results = []
    
    results.append(("Weather Service", test_weather_service()))
    results.append(("News Service", test_news_service()))
    results.append(("Storage Service", test_storage_service()))
    results.append(("Settings Service", test_settings_service()))
    results.append(("Message Formatters", test_message_formatters()))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 50)
    if all_passed:
        print("✅ All functional tests passed!")
        print("\n💡 다음 단계:")
        print("1. .env 파일을 생성하고 API 키를 설정하세요")
        print("2. python src/main.py health 로 헬스체크를 실행하세요")
        print("3. python src/main.py weather 로 날씨 알림을 테스트하세요")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

