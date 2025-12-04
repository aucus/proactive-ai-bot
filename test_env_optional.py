#!/usr/bin/env python3
"""Test which environment variables are required vs optional"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_without_optional_keys():
    """Test behavior when optional keys are missing"""
    print("=" * 60)
    print("환경변수 선택적 동작 테스트")
    print("=" * 60)
    
    # Clear all optional env vars
    optional_vars = [
        "OPENWEATHER_API_KEY",
        "NEWS_API_KEY",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REFRESH_TOKEN",
        "GIST_TOKEN",
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "OBSIDIAN_VAULT_PATH",
        "YOUTUBE_API_KEY"
    ]
    
    for var in optional_vars:
        if var in os.environ:
            del os.environ[var]
    
    print("\n✅ 선택적 환경변수 제거 완료\n")
    
    # Test each service
    results = {}
    
    # 1. Weather Service
    print("1. Weather Service 테스트...")
    try:
        from src.services.weather import get_weather
        result = get_weather()
        if result is None:
            results["weather"] = "✅ 정상 (API 키 없으면 None 반환, 에러 없음)"
        else:
            results["weather"] = "✅ 정상 (데이터 반환)"
    except Exception as e:
        results["weather"] = f"❌ 실패: {e}"
    print(f"   {results['weather']}\n")
    
    # 2. News Service
    print("2. News Service 테스트...")
    try:
        from src.services.news import get_news_briefing
        result = get_news_briefing(max_items=3)
        if result:
            results["news"] = f"✅ 정상 (RSS fallback 작동, {len(result)}개 항목)"
        else:
            results["news"] = "⚠️ 빈 결과 (하지만 에러 없음)"
    except Exception as e:
        results["news"] = f"❌ 실패: {e}"
    print(f"   {results['news']}\n")
    
    # 3. Calendar Service
    print("3. Calendar Service 테스트...")
    try:
        from src.services.calendar import get_today_events
        result = get_today_events()
        if result == []:
            results["calendar"] = "✅ 정상 (OAuth 없으면 빈 리스트 반환, 에러 없음)"
        else:
            results["calendar"] = f"✅ 정상 (데이터 반환: {len(result)}개)"
    except Exception as e:
        results["calendar"] = f"❌ 실패: {e}"
    print(f"   {results['calendar']}\n")
    
    # 4. Storage Service
    print("4. Storage Service 테스트...")
    try:
        from src.utils.storage import save_state
        result = save_state({"test": "data"})
        if result is None:
            results["storage"] = "✅ 정상 (Gist 토큰 없으면 None 반환, 에러 없음)"
        else:
            results["storage"] = f"✅ 정상 (Gist ID: {result})"
    except Exception as e:
        results["storage"] = f"❌ 실패: {e}"
    print(f"   {results['storage']}\n")
    
    # 5. Settings Service
    print("5. Settings Service 테스트...")
    try:
        from src.utils.settings import load_settings
        result = load_settings()
        if result:
            results["settings"] = f"✅ 정상 (기본 설정 로드: {len(result)}개 키)"
        else:
            results["settings"] = "❌ 실패 (설정 로드 안됨)"
    except Exception as e:
        results["settings"] = f"❌ 실패: {e}"
    print(f"   {results['settings']}\n")
    
    # 6. Projects Service
    print("6. Projects Service 테스트...")
    try:
        from src.services.projects import get_project_reminders
        result = get_project_reminders()
        if result:
            results["projects"] = f"✅ 정상 (플레이스홀더 메시지 반환)"
        else:
            results["projects"] = "❌ 실패"
    except Exception as e:
        results["projects"] = f"❌ 실패: {e}"
    print(f"   {results['projects']}\n")
    
    # Summary
    print("=" * 60)
    print("요약:")
    print("=" * 60)
    for service, result in results.items():
        print(f"{service.capitalize()}: {result}")
    
    all_ok = all("✅" in r or "⚠️" in r for r in results.values())
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ 모든 선택적 환경변수가 없어도 정상 동작합니다!")
        print("\n💡 필수 환경변수:")
        print("   - TELEGRAM_TOKEN (실제 메시지 전송용)")
        print("   - TELEGRAM_CHAT_ID (실제 메시지 전송용)")
        print("   - GEMINI_API_KEY (LLM 기능용)")
        print("\n💡 선택적 환경변수:")
        print("   - 나머지는 모두 선택사항입니다")
        print("   - 없으면 해당 기능만 비활성화되거나 fallback 사용")
    else:
        print("❌ 일부 서비스에서 문제가 발생했습니다")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(test_without_optional_keys())

