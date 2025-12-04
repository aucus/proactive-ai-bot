"""Message formatting utilities"""


def format_commute_message(commute_data: dict, llm_text: str = None) -> str:
    """
    Format commute weather message with home and office weather
    
    Args:
        commute_data: Dictionary with 'home', 'office', 'home_location', 'office_location'
        llm_text: Optional LLM-generated text
    
    Returns:
        Formatted message string
    """
    if llm_text:
        return llm_text
    
    home_weather = commute_data.get("home")
    office_weather = commute_data.get("office")
    home_location = commute_data.get("home_location", {})
    office_location = commute_data.get("office_location", {})
    
    home_name = home_location.get("display_name", "집")
    office_name = office_location.get("display_name", "회사")
    
    message = f"🚗 출근 준비 알림\n\n"
    
    if home_weather:
        temp = home_weather.get("temp", "N/A")
        feels_like = home_weather.get("feels_like", "N/A")
        description = home_weather.get("description", "")
        rain_prob = home_weather.get("rain_probability", 0)
        
        message += f"📍 {home_name} 날씨:\n"
        message += f"- {temp}°C (체감 {feels_like}°C)\n"
        message += f"- {description}\n"
        message += f"- 강수확률 {rain_prob}%\n\n"
    else:
        message += f"📍 {home_name} 날씨 정보를 가져올 수 없어요\n\n"
    
    if office_weather:
        temp = office_weather.get("temp", "N/A")
        feels_like = office_weather.get("feels_like", "N/A")
        description = office_weather.get("description", "")
        rain_prob = office_weather.get("rain_probability", 0)
        
        message += f"📍 {office_name} 날씨:\n"
        message += f"- {temp}°C (체감 {feels_like}°C)\n"
        message += f"- {description}\n"
        message += f"- 강수확률 {rain_prob}%\n\n"
    else:
        message += f"📍 {office_name} 날씨 정보를 가져올 수 없어요\n\n"
    
    # Add umbrella recommendation
    max_rain_prob = max(
        home_weather.get("rain_probability", 0) if home_weather else 0,
        office_weather.get("rain_probability", 0) if office_weather else 0
    )
    
    if max_rain_prob >= 30:
        message += "☂️ 우산을 챙기세요!"
    else:
        message += "☂️ 우산은 필요 없어요"
    
    return message


def format_weather_message(weather_data: dict, llm_text: str = None) -> str:
    """
    Format weather message
    
    Args:
        weather_data: Weather data dictionary
        llm_text: Optional LLM-generated text
    
    Returns:
        Formatted message string
    """
    if llm_text:
        return llm_text
    
    # Fallback formatting
    temp = weather_data.get("temp", "N/A")
    feels_like = weather_data.get("feels_like", "N/A")
    description = weather_data.get("description", "")
    humidity = weather_data.get("humidity", "N/A")
    rain_prob = weather_data.get("rain_probability", 0)
    
    message = f"🌤 좋은 아침이에요!\n\n"
    message += f"오늘 서울 날씨:\n"
    message += f"- 현재 {temp}°C (체감 {feels_like}°C)\n"
    message += f"- {description}\n"
    message += f"- 강수확률 {rain_prob}%\n"
    
    if rain_prob >= 30:
        message += f"\n☂️ 우산을 챙기세요!"
    else:
        message += f"\n☂️ 우산은 필요 없어요"
    
    return message


def format_news_message(news_items: list) -> str:
    """
    Format news briefing message
    
    Args:
        news_items: List of news items
    
    Returns:
        Formatted message string
    """
    message = "📰 오늘의 테크 뉴스\n\n"
    
    for i, item in enumerate(news_items[:5], 1):
        title = item.get("title", "")
        summary = item.get("summary", "")
        url = item.get("url", "")
        category = item.get("category", "News")
        
        message += f"{i}️⃣ [{category}] {title}\n"
        if summary:
            # Limit summary length for Telegram
            summary_text = summary[:150] if len(summary) > 150 else summary
            message += f"   {summary_text}\n"
        if url:
            message += f"   🔗 {url}\n"
        message += "\n"
    
    return message


def format_schedule_message(events: list) -> str:
    """
    Format schedule briefing message
    
    Args:
        events: List of calendar events
    
    Returns:
        Formatted message string
    """
    message = "📅 오늘 일정 브리핑\n\n"
    
    if not events:
        message += "오늘 예정된 일정이 없어요! 😊"
        return message
    
    # Sort by time if available
    sorted_events = sorted(events, key=lambda e: e.get("start", "") or "")
    
    for event in sorted_events:
        time = event.get("time", "시간 미정")
        title = event.get("title", "제목 없음")
        location = event.get("location", "")
        important = event.get("important", False)
        
        # Mark important events
        prefix = "⭐ " if important else ""
        message += f"{prefix}{time} - {title}"
        if location:
            message += f" ({location})"
        message += "\n"
    
    return message


def format_evening_message(briefing: dict) -> str:
    """
    Format evening reminder message
    
    Args:
        briefing: Evening briefing dictionary
    
    Returns:
        Formatted message string
    """
    message = "🌆 퇴근 시간 알림\n\n"
    
    schedule = briefing.get("schedule", {})
    evening_events = schedule.get("evening_events", [])
    tomorrow_preview = schedule.get("tomorrow_preview", [])
    
    # Evening events
    if evening_events:
        message += "📅 오늘 저녁 일정:\n"
        for event in evening_events[:5]:
            time = event.get("time", "시간 미정")
            title = event.get("title", "제목 없음")
            location = event.get("location", "")
            
            message += f"- {time} {title}"
            if location:
                message += f" ({location})"
            message += "\n"
        message += "\n"
    else:
        message += "오늘 저녁 예정된 일정이 없어요! 😊\n\n"
    
    # Tomorrow preview
    if tomorrow_preview:
        message += "📆 내일 주요 일정 미리보기:\n"
        for event in tomorrow_preview:
            time = event.get("time", "시간 미정")
            title = event.get("title", "제목 없음")
            message += f"- {time} {title}\n"
        message += "\n"
    
    # Content recommendations
    recommendations = briefing.get("recommendations", [])
    if recommendations:
        message += "💡 퇴근길 추천:\n"
        for rec in recommendations[:2]:
            rec_type = "📰" if rec.get("type") == "article" else "🎬"
            title = rec.get("title", "")
            description = rec.get("description", "")
            message += f"{rec_type} {title}\n"
            if description:
                message += f"   {description}\n"
        message += "\n"
    
    message += "오늘 하루도 수고하셨어요! 🌙"
    
    return message


def format_project_message(reminders: dict) -> str:
    """
    Format project reminder message
    
    Args:
        reminders: Project reminders dictionary
    
    Returns:
        Formatted message string
    """
    message = "🌙 저녁 프로젝트 리마인더\n\n"
    
    projects = reminders.get("projects", [])
    has_projects = reminders.get("has_projects", False)
    
    if not has_projects or not projects:
        fallback_message = reminders.get("message", "현재 진행 중인 프로젝트가 없어요. 새로운 프로젝트를 시작해볼까요? 🚀")
        message += fallback_message
        return message
    
    message += f"진행 중인 프로젝트 {len(projects)}개:\n\n"
    
    for i, project in enumerate(projects[:5], 1):
        title = project.get("title", "제목 없음")
        next_actions = project.get("next_actions", [])
        
        message += f"{i}️⃣ **{title}**\n"
        
        if next_actions:
            message += "   다음 액션:\n"
            for action in next_actions[:3]:
                message += f"   - {action}\n"
        else:
            message += "   다음 액션을 추가해보세요! ✨\n"
        
        message += "\n"
    
    message += "오늘 저녁 시간을 활용해서 조금씩 진행해보세요! 💪"
    
    return message



