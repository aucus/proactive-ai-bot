# 배포 가이드 (Deployment Guide)

## 실제 구동을 위한 단계

### 1단계: Git Repository 초기화 및 GitHub 연결

```bash
# Git 초기화
git init
git add .
git commit -m "Initial commit: Proactive AI Bot"

# GitHub Repository 생성 (또는 기존 repository 사용)
# 옵션 A: GitHub CLI 사용
gh repo create proactive-ai-bot --public --source=. --remote=origin

# 옵션 B: 수동으로 GitHub에서 생성 후
git remote add origin https://github.com/YOUR_USERNAME/proactive-ai-bot.git
git branch -M main
git push -u origin main
```

### 2단계: GitHub Secrets 설정

GitHub Repository → Settings → Secrets and variables → Actions → New repository secret

**필수 Secrets:**
- `TELEGRAM_TOKEN`: Telegram Bot 토큰
- `TELEGRAM_CHAT_ID`: Telegram Chat ID
- `GEMINI_API_KEY`: Gemini API 키

**선택 Secrets:**
- `OPENWEATHER_API_KEY`: 날씨 API (없으면 웹 fallback 사용)
- `NEWS_API_KEY`: 뉴스 API (없으면 RSS 사용)
- `GOOGLE_CLIENT_ID`: Google Calendar용
- `GOOGLE_CLIENT_SECRET`: Google Calendar용
- `GOOGLE_REFRESH_TOKEN`: Google Calendar용
- `GIST_TOKEN`: 상태 저장용
- `QDRANT_URL`: 프로젝트 리마인더용
- `QDRANT_API_KEY`: 프로젝트 리마인더용
- `OBSIDIAN_VAULT_PATH`: 프로젝트 리마인더용

### 3단계: GitHub Actions Workflow 테스트

각 Workflow를 수동으로 실행하여 테스트:

1. **Repository → Actions 탭**
2. **각 Workflow 선택** (Morning Weather, Morning News 등)
3. **Run workflow 버튼 클릭**
4. **실행 결과 확인**

### 4단계: 스케줄 확인

Workflow가 다음 시간에 자동 실행됩니다:

- **07:00 KST**: 날씨 알림 (`morning-weather.yml`)
- **08:00 KST**: 뉴스 브리핑 (`morning-news.yml`)
- **09:30 KST**: 일정 브리핑 (`work-schedule.yml`) - 평일만
- **18:00 KST**: 퇴근 알림 (`evening-reminder.yml`) - 평일만
- **21:00 KST**: 프로젝트 리마인더 (`night-project.yml`)

### 5단계: 모니터링

- **Actions 탭**: Workflow 실행 로그 확인
- **Telegram**: 실제 메시지 수신 확인
- **헬스체크**: `python src/main.py health` 명령어로 주기적 확인

## 빠른 시작 스크립트

```bash
#!/bin/bash
# deploy.sh

echo "🚀 Proactive AI Bot 배포 시작..."

# 1. Git 초기화
if [ ! -d .git ]; then
    echo "📦 Git 초기화..."
    git init
    git add .
    git commit -m "Initial commit: Proactive AI Bot"
fi

# 2. GitHub Repository 확인
if ! git remote | grep -q origin; then
    echo "⚠️  GitHub Repository를 먼저 생성하고 연결하세요:"
    echo "   gh repo create proactive-ai-bot --public --source=. --remote=origin"
    exit 1
fi

# 3. 푸시
echo "📤 코드 푸시..."
git push -u origin main

echo "✅ 배포 완료!"
echo ""
echo "다음 단계:"
echo "1. GitHub Repository → Settings → Secrets에 API 키 설정"
echo "2. Actions 탭에서 Workflow 수동 실행 테스트"
echo "3. 스케줄 실행 확인"
```

## 문제 해결

### Workflow 실행 실패 시
1. **Secrets 확인**: 모든 필수 Secrets가 설정되었는지 확인
2. **로그 확인**: Actions 탭에서 상세 에러 로그 확인
3. **로컬 테스트**: `python src/main.py [command]` 로컬에서 먼저 테스트

### 메시지가 전송되지 않을 때
1. **TELEGRAM_TOKEN 확인**: @BotFather에서 토큰 확인
2. **TELEGRAM_CHAT_ID 확인**: @userinfobot으로 chat_id 확인
3. **봇과 대화**: 봇에게 `/start` 메시지 전송 필요

---
*Last Updated: 2025-12-04*

