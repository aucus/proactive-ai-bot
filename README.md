# Proactive AI Telegram Bot

> 능동적으로 알려주고 소통하는 나만의 AI 서비스

## 🎯 Project Vision

시간대별로 필요한 정보를 **먼저 알려주는** 개인 AI 비서
- 아침: 날씨 + 옷차림 추천
- 출근길: 관심사 뉴스 브리핑
- 출근 후: 일정 보고 + 토픽 분석
- 퇴근: 저녁 일정 + 콘텐츠 추천
- 저녁: 개인 프로젝트 리마인드 + 엔터테인먼트

## 🚀 빠른 시작

### 로컬 개발 환경

```bash
# 저장소 클론
git clone <repository-url>
cd proactive-ai-bot

# 가상환경 설정
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### GitHub Actions 배포

```bash
# 배포 스크립트 실행
./deploy.sh

# 또는 수동으로
git init
git add .
git commit -m "Initial commit"
gh repo create proactive-ai-bot --public --source=. --remote=origin
git push -u origin main
```

자세한 배포 가이드는 [SETUP_GITHUB.md](./SETUP_GITHUB.md) 참조

### 2. 환경변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```bash
# 필수
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
GEMINI_API_KEY=your_gemini_api_key

# 선택
OPENWEATHER_API_KEY=your_openweather_api_key
NEWS_API_KEY=your_news_api_key
GIST_TOKEN=your_github_gist_token
```

### 3. 테스트 실행

```bash
# 기본 테스트
python3 test_basic.py

# 기능 테스트
python3 test_functional.py

# 헬스체크
python3 src/main.py health
```

### 4. 명령어 실행

```bash
# 날씨 알림
python3 src/main.py weather

# 뉴스 브리핑
python3 src/main.py news

# 일정 브리핑
python3 src/main.py schedule

# 저녁 알림
python3 src/main.py evening

# 프로젝트 리마인더
python3 src/main.py night

# Polling 모드 (대화형)
python3 src/main.py poll
```

## 📋 Related Documents

- [[PRD - Proactive AI Telegram Bot]] - 제품 요구사항
- [[Architecture - Proactive AI Telegram Bot]] - 기술 아키텍처
- [[Development Tasks - Proactive AI Telegram Bot]] - 개발 태스크

## 🔗 Quick Links

- Telegram Bot API: https://core.telegram.org/bots/api
- Gemini API: https://ai.google.dev/
- OpenWeatherMap API: https://openweathermap.org/api

---
*Last Updated: 2025-12-04*
