"""Telegram bot command handlers"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from src.services.weather import get_weather
from src.services.llm import generate_weather_message
from src.bot.messages import format_weather_message
from src.services.news import get_news_briefing
from src.bot.messages import format_news_message
from src.services.calendar import get_schedule_briefing
from src.bot.messages import format_schedule_message
from src.services.projects import get_project_reminders
from src.bot.messages import format_project_message
from src.bot.telegram import send_message_sync
from src.utils.settings import is_notification_enabled

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    message = """안녕하세요! 👋

저는 능동적으로 정보를 알려주는 AI 비서예요.

📋 사용 가능한 명령어:
/weather - 현재 날씨 확인
/news [topic] - 뉴스 브리핑 (topic: ai, tech, edtech)
/schedule - 오늘 일정 확인
/project - 프로젝트 현황
/settings - 설정 확인
/help - 도움말

자동 알림:
🌤 07:00 - 날씨 알림
📰 08:00 - 뉴스 브리핑
📅 09:30 - 일정 브리핑 (평일)
🌆 18:00 - 퇴근 알림 (평일)
🌙 21:00 - 프로젝트 리마인더"""
    
    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    message = """📖 도움말

명령어 목록:
/start - 시작하기
/weather - 현재 날씨 확인
/news [topic] - 뉴스 브리핑
  • topic: ai, tech, edtech (선택)
/schedule - 오늘 일정 확인
/project - 프로젝트 현황
/settings - 설정 확인
/help - 이 도움말

자동 알림은 매일 지정된 시간에 자동으로 전송됩니다.
설정 변경은 /settings 명령어로 가능합니다."""
    
    await update.message.reply_text(message)


async def weather_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /weather command"""
    await update.message.reply_text("날씨 정보를 가져오는 중...")
    
    try:
        weather_data = get_weather()
        if not weather_data:
            await update.message.reply_text("날씨 정보를 가져올 수 없어요. 잠시 후 다시 시도해주세요.")
            return
        
        llm_message = generate_weather_message(weather_data)
        if llm_message:
            message = llm_message
        else:
            message = format_weather_message(weather_data)
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Weather command failed: {e}")
        await update.message.reply_text("날씨 정보를 가져오는 중 오류가 발생했어요.")


async def news_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /news command"""
    await update.message.reply_text("뉴스를 가져오는 중...")
    
    try:
        # Get topic from command args if provided
        topic = None
        if context.args:
            topic = context.args[0].lower()
        
        news_items = get_news_briefing(max_items=5)
        if not news_items:
            await update.message.reply_text("뉴스를 가져올 수 없어요. 잠시 후 다시 시도해주세요.")
            return
        
        message = format_news_message(news_items)
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"News command failed: {e}")
        await update.message.reply_text("뉴스를 가져오는 중 오류가 발생했어요.")


async def schedule_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /schedule command"""
    await update.message.reply_text("일정을 확인하는 중...")
    
    try:
        from src.services.calendar import is_calendar_configured
        if not is_calendar_configured():
            await update.message.reply_text("📅 오늘 일정 브리핑\n\n구글 캘린더 연동이 설정되지 않았어요. (GOOGLE_* 시크릿 확인 필요)")
            return

        schedule_data = get_schedule_briefing()
        events = schedule_data.get("events", [])
        
        if not events:
            message = "📅 오늘 일정 브리핑\n\n오늘 예정된 일정이 없어요! 😊"
        else:
            message = format_schedule_message(events)
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Schedule command failed: {e}")
        await update.message.reply_text("일정을 가져오는 중 오류가 발생했어요.")


async def project_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /project command"""
    await update.message.reply_text("프로젝트 정보를 확인하는 중...")
    
    try:
        reminders = get_project_reminders()
        message = format_project_message(reminders)
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Project command failed: {e}")
        await update.message.reply_text("프로젝트 정보를 가져오는 중 오류가 발생했어요.")


async def settings_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command"""
    try:
        from src.utils.settings import load_settings
        
        settings = load_settings()
        
        message = "⚙️ 현재 설정\n\n"
        message += "알림 설정:\n"
        for notif_type, enabled in settings.get("notifications", {}).items():
            emoji = "✅" if enabled else "❌"
            message += f"{emoji} {notif_type.capitalize()}\n"
        
        message += f"\n위치: {settings.get('location', {}).get('city', 'Seoul')}\n"
        message += f"뉴스 카테고리: {', '.join(settings.get('news_categories', []))}\n"
        message += "\n설정 변경은 아직 지원되지 않아요. 곧 추가될 예정입니다! 🚀"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Settings command failed: {e}")
        await update.message.reply_text("설정을 불러오는 중 오류가 발생했어요.")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text("알 수 없는 명령어예요. /help를 입력하면 사용 가능한 명령어를 확인할 수 있어요.")

