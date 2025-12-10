"""Main entry point for the bot"""

import sys
import time
import logging
import argparse
from src.services.weather import get_weather
from src.services.llm import generate_weather_message
from src.bot.messages import format_weather_message
from src.bot.telegram import send_message_sync
from src.utils.logger import setup_logging, log_execution
from src.utils.monitoring import health_check

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)


def weather_command():
    """Handle weather notification command"""
    start_time = time.time()
    logger.info("Starting weather notification...")
    
    try:
        # Get weather data
        weather_data = get_weather()
        if not weather_data:
            logger.error("Failed to get weather data")
            log_execution("weather", False, time.time() - start_time)
            return 1
        
        # Generate message with LLM
        llm_message = generate_weather_message(weather_data)
        
        # Format message
        if llm_message:
            message = llm_message
        else:
            message = format_weather_message(weather_data)
        
        # Send to Telegram
        success = send_message_sync(message)
        
        duration = time.time() - start_time
        log_execution("weather", success, duration)
        
        if success:
            logger.info("Weather notification sent successfully")
            return 0
        else:
            logger.error("Failed to send weather notification")
            return 1
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Weather command failed: {e}", exc_info=True)
        log_execution("weather", False, duration)
        return 1


def news_command():
    """Handle news briefing command"""
    logger.info("Starting news briefing...")
    
    from src.services.news import get_news_briefing
    from src.bot.messages import format_news_message
    from src.utils.config import NEWS_API_KEY
    
    try:
        # Get news briefing
        news_items = get_news_briefing(max_items=5)
        if not news_items:
            logger.warning("No news items retrieved")
            # Check if API key is configured
            api_status = "설정됨" if NEWS_API_KEY else "미설정"
            logger.warning(f"News API key status: {api_status}")
            # Send fallback message
            message = "📰 오늘의 뉴스\n\n뉴스를 가져오는 중 문제가 발생했어요. 잠시 후 다시 시도해주세요."
            success = send_message_sync(message)
            return 0 if success else 1
        
        # Format message
        message = format_news_message(news_items)
        
        # Send to Telegram
        success = send_message_sync(message)
        
        if success:
            logger.info(f"News briefing sent successfully with {len(news_items)} items")
            return 0
        else:
            logger.error("Failed to send news briefing")
            return 1
    except Exception as e:
        logger.error(f"News command failed: {e}", exc_info=True)
        # Send error message
        message = "📰 오늘의 뉴스\n\n뉴스를 가져오는 중 오류가 발생했어요. 잠시 후 다시 시도해주세요."
        send_message_sync(message)
        return 1


def schedule_command():
    """Handle schedule briefing command"""
    start_time = time.time()
    from datetime import datetime, timezone, timedelta
    
    # Log current time in both UTC and KST
    now_utc = datetime.now(timezone.utc)
    kst = timezone(timedelta(hours=9))
    now_kst = now_utc.astimezone(kst)
    
    logger.info("=" * 60)
    logger.info("Starting schedule briefing...")
    logger.info(f"Current time (UTC): {now_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Current time (KST): {now_kst.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    from src.services.calendar import get_schedule_briefing
    from src.bot.messages import format_schedule_message
    from src.services.llm import generate_text
    
    # Get schedule briefing
    schedule_data = get_schedule_briefing()
    events = schedule_data.get("events", [])
    total_count = schedule_data.get("count", 0)
    
    logger.info(f"Schedule briefing result: {len(events)} events, total count: {total_count}")
    
    if not events:
        logger.warning("No events found for today after filtering")
        # Log additional debug info
        from src.services.calendar import get_today_events
        all_today_events = get_today_events()
        logger.info(f"Total events retrieved from API: {len(all_today_events)}")
        if all_today_events:
            logger.info(f"First event: {all_today_events[0].get('title')} at {all_today_events[0].get('start')}")
        
        # Send message even if no events
        message = "📅 오늘 일정 브리핑\n\n오늘 예정된 일정이 없어요! 😊"
        success = send_message_sync(message)
        return 0 if success else 1
    
    # Format message
    message = format_schedule_message(events)
    
    # Optionally enhance with LLM
    if schedule_data.get("important_count", 0) > 0:
        try:
            events_text = "\n".join([
                f"- {e.get('time', '')} {e.get('title', '')}"
                for e in events[:5]
            ])
            llm_prompt = f"""다음 오늘 일정을 바탕으로 친근하고 자연스러운 브리핑 메시지를 작성해주세요.
한국어로 작성하고, 중요 일정이 있으면 강조해주세요.

일정:
{events_text}

기존 메시지 형식은 유지하면서 자연스럽게 개선해주세요."""
            
            enhanced_message = generate_text(llm_prompt)
            if enhanced_message:
                message = enhanced_message
        except Exception as e:
            logger.warning(f"Failed to enhance message with LLM: {e}")
    
    # Send to Telegram
    success = send_message_sync(message)
    
    duration = time.time() - start_time
    log_execution("schedule", success, duration)
    
    if success:
        logger.info(f"Schedule briefing sent successfully (took {duration:.2f}s)")
        logger.info(f"Sent at KST: {now_kst.strftime('%Y-%m-%d %H:%M:%S')}")
        return 0
    else:
        logger.error("Failed to send schedule briefing")
        return 1


def evening_command():
    """Handle evening reminder command"""
    logger.info("Starting evening reminder...")
    
    from src.services.evening import get_evening_briefing
    from src.bot.messages import format_evening_message
    from src.services.llm import generate_text
    
    # Get evening briefing
    briefing = get_evening_briefing()
    
    # Format message
    message = format_evening_message(briefing)
    
    # Optionally enhance with LLM
    try:
        schedule_info = briefing.get("schedule", {})
        if schedule_info.get("has_evening_plans") or schedule_info.get("has_tomorrow_important"):
            llm_prompt = f"""다음 퇴근 시간 정보를 바탕으로 친근하고 자연스러운 저녁 알림 메시지를 작성해주세요.
한국어로 작성하고, 이모지를 적절히 사용해주세요.

저녁 일정: {len(schedule_info.get('evening_events', []))}개
내일 중요 일정: {len(schedule_info.get('tomorrow_preview', []))}개

기존 메시지 형식은 유지하면서 자연스럽게 개선해주세요."""
            
            enhanced_message = generate_text(llm_prompt)
            if enhanced_message:
                # Combine with original message
                message = enhanced_message + "\n\n" + message.split("\n\n", 1)[-1] if "\n\n" in message else message
    except Exception as e:
        logger.warning(f"Failed to enhance message with LLM: {e}")
    
    # Send to Telegram
    success = send_message_sync(message)
    
    if success:
        logger.info("Evening reminder sent successfully")
        return 0
    else:
        logger.error("Failed to send evening reminder")
        return 1


def night_command():
    """Handle night project reminder command"""
    logger.info("Starting night project reminder...")
    
    from src.services.projects import get_project_reminders
    from src.bot.messages import format_project_message
    from src.services.llm import generate_text
    
    # Get project reminders
    reminders = get_project_reminders()
    
    # Format message
    message = format_project_message(reminders)
    
    # Optionally enhance with LLM if there are projects
    if reminders.get("has_projects"):
        try:
            projects_text = "\n".join([
                f"- {p.get('title', '')}: {', '.join(p.get('next_actions', [])[:2])}"
                for p in reminders.get("projects", [])[:3]
            ])
            llm_prompt = f"""다음 진행 중인 프로젝트 정보를 바탕으로 친근하고 자연스러운 저녁 프로젝트 리마인더 메시지를 작성해주세요.
한국어로 작성하고, 이모지를 적절히 사용해주세요. 다음 액션을 제안하는 톤으로 작성해주세요.

프로젝트:
{projects_text}

기존 메시지 형식은 유지하면서 자연스럽게 개선해주세요."""
            
            enhanced_message = generate_text(llm_prompt)
            if enhanced_message:
                # Combine with original message
                message = enhanced_message + "\n\n" + message.split("\n\n", 1)[-1] if "\n\n" in message else message
        except Exception as e:
            logger.warning(f"Failed to enhance message with LLM: {e}")
    
    # Send to Telegram
    success = send_message_sync(message)
    
    if success:
        logger.info("Night project reminder sent successfully")
        return 0
    else:
        logger.error("Failed to send night project reminder")
        return 1


def commute_command():
    """Handle commute notification command"""
    start_time = time.time()
    logger.info("Starting commute notification...")
    
    try:
        from src.services.commute import get_commute_weather
        from src.bot.messages import format_commute_message
        from src.services.llm import generate_text
        
        # Get commute weather (home and office)
        commute_data = get_commute_weather()
        
        if not commute_data.get("home") and not commute_data.get("office"):
            logger.error("Failed to get commute weather data")
            log_execution("commute", False, time.time() - start_time)
            return 1
        
        # Format message
        message = format_commute_message(commute_data)
        
        # Optionally enhance with LLM
        try:
            home_weather = commute_data.get("home", {})
            office_weather = commute_data.get("office", {})
            home_name = commute_data.get("home_location", {}).get("display_name", "집")
            office_name = commute_data.get("office_location", {}).get("display_name", "회사")
            
            if home_weather and office_weather:
                llm_prompt = f"""다음 출근 준비 알림을 바탕으로 친근하고 자연스러운 메시지를 작성해주세요.
한국어로 작성하고, 이모지를 적절히 사용해주세요.

{home_name} 날씨: {home_weather.get('temp', 'N/A')}°C, {home_weather.get('description', '')}, 강수확률 {home_weather.get('rain_probability', 0)}%
{office_name} 날씨: {office_weather.get('temp', 'N/A')}°C, {office_weather.get('description', '')}, 강수확률 {office_weather.get('rain_probability', 0)}%

출근 준비를 도와주는 톤으로 작성해주세요."""
                
                enhanced_message = generate_text(llm_prompt)
                if enhanced_message:
                    message = enhanced_message
        except Exception as e:
            logger.warning(f"Failed to enhance message with LLM: {e}")
        
        # Send to Telegram
        success = send_message_sync(message)
        
        duration = time.time() - start_time
        log_execution("commute", success, duration)
        
        if success:
            logger.info("Commute notification sent successfully")
            return 0
        else:
            logger.error("Failed to send commute notification")
            return 1
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Commute command failed: {e}", exc_info=True)
        log_execution("commute", False, duration)
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Proactive AI Telegram Bot")
    parser.add_argument(
        "command",
        choices=["weather", "news", "schedule", "evening", "night", "health", "poll", "commute"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    # Polling mode
    if args.command == "poll":
        from src.bot.polling import run_polling
        run_polling()
        return 0
    
    # Health check command
    if args.command == "health":
        from src.utils.monitoring import send_health_report
        if health_check():
            logger.info("Health check passed")
            send_health_report()
            return 0
        else:
            logger.error("Health check failed")
            return 1
    
    # Run health check before other commands
    if not health_check():
        logger.warning("Health check failed, but continuing...")
    
    if args.command == "weather":
        return weather_command()
    elif args.command == "commute":
        return commute_command()
    elif args.command == "news":
        return news_command()
    elif args.command == "schedule":
        return schedule_command()
    elif args.command == "evening":
        return evening_command()
    elif args.command == "night":
        return night_command()
    else:
        logger.warning(f"Command '{args.command}' not implemented yet")
        return 0


if __name__ == "__main__":
    sys.exit(main())



