#!/usr/bin/env python3
"""Basic tests for the bot"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.utils.logger import setup_logging
        print("✅ Logger module OK")
    except Exception as e:
        print(f"❌ Logger module failed: {e}")
        return False
    
    try:
        from src.utils.retry import retry_on_failure
        print("✅ Retry module OK")
    except Exception as e:
        print(f"❌ Retry module failed: {e}")
        return False
    
    try:
        from src.utils.storage import save_state, load_state
        print("✅ Storage module OK")
    except Exception as e:
        print(f"❌ Storage module failed: {e}")
        return False
    
    try:
        from src.utils.settings import load_settings
        print("✅ Settings module OK")
    except Exception as e:
        print(f"❌ Settings module failed: {e}")
        return False
    
    try:
        from src.bot.messages import format_weather_message
        print("✅ Messages module OK")
    except Exception as e:
        print(f"❌ Messages module failed: {e}")
        return False
    
    return True


def test_config_without_env():
    """Test config module without required env vars"""
    print("\nTesting config module (without env vars)...")
    
    try:
        # This should fail gracefully
        from src.utils.config import get_env
        try:
            get_env("NON_EXISTENT_KEY")
            print("❌ Config should fail for missing keys")
            return False
        except ValueError:
            print("✅ Config properly validates required keys")
            return True
    except Exception as e:
        print(f"❌ Config module failed: {e}")
        return False


def test_message_formatting():
    """Test message formatting functions"""
    print("\nTesting message formatting...")
    
    try:
        from src.bot.messages import format_weather_message, format_news_message
        
        # Test weather message
        weather_data = {
            "temp": 15,
            "feels_like": 12,
            "description": "맑음",
            "rain_probability": 10
        }
        message = format_weather_message(weather_data)
        if message and len(message) > 0:
            print("✅ Weather message formatting OK")
        else:
            print("❌ Weather message formatting failed")
            return False
        
        # Test news message
        news_items = [
            {"title": "Test News", "summary": "Test summary", "url": "https://test.com", "category": "Tech"}
        ]
        message = format_news_message(news_items)
        if message and len(message) > 0:
            print("✅ News message formatting OK")
        else:
            print("❌ News message formatting failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Message formatting failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Basic Tests for Proactive AI Bot")
    print("=" * 50)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Config", test_config_without_env()))
    results.append(("Message Formatting", test_message_formatting()))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 50)
    if all_passed:
        print("✅ All basic tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

