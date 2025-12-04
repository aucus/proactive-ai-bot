# Development Tasks - Proactive AI Telegram Bot

## 📊 Progress Overview

| Phase | 상태 | 진행률 | 기간 |
|-------|------|--------|------|
| Phase 1: MVP | 🚧 진행중 | 60% | 2주 |
| Phase 2: Core | 🚧 진행중 | 70% | 3주 |
| Phase 3: Enhancement | 🚧 진행중 | 80% | 2주 |

---

## Phase 1: MVP (Week 1-2)

### 1.1 GitHub Actions 셋업

- [ ] **Repository 생성** (다음 단계)
  - Priority: 🔴 Critical
  - `proactive-ai-bot` (Public)
  - GitHub Actions 활성화
  - `deploy.sh` 스크립트 생성 완료 ✅

- [x] **Workflow 파일 생성** ✅
  ```
  .github/workflows/
  ├── morning-weather.yml    # 07:00 KST (cron: 0 22 * * *) ✅ 완료
  ├── morning-news.yml       # 08:00 KST (cron: 0 23 * * *) ✅ 완료
  ├── work-schedule.yml      # 09:30 KST (cron: 30 0 * * 1-5) ✅ 완료
  ├── evening-reminder.yml   # 18:00 KST (cron: 0 9 * * 1-5) ✅ 완료
  └── night-project.yml      # 21:00 KST (cron: 0 12 * * *) ✅ 완료
  ```

- [ ] **GitHub Secrets 설정**
  - TELEGRAM_TOKEN
  - TELEGRAM_CHAT_ID
  - GEMINI_API_KEY
  - OPENWEATHER_API_KEY
  - NEWS_API_KEY (선택, 없으면 RSS 사용)

### 1.2 Python 프로젝트 구조

- [x] **기본 디렉토리 구조 생성** ✅
  ```
  src/
  ├── __init__.py ✅
  ├── main.py                    # CLI 엔트리포인트 ✅
  ├── bot/
  │   ├── __init__.py ✅
  │   ├── telegram.py            # Telegram 전송 ✅
  │   ├── messages.py            # 메시지 포맷팅 ✅
  │   ├── handlers.py            # 명령어 핸들러 ✅
  │   └── polling.py             # Polling 서비스 ✅
  ├── services/
  │   ├── __init__.py ✅
  │   ├── weather.py             # 날씨 API ✅
  │   ├── news.py                # 뉴스 수집 ✅
  │   ├── calendar.py            # Google Calendar ✅
  │   ├── llm.py                 # Gemini API ✅
  │   ├── evening.py             # 저녁 알림 ✅
  │   └── projects.py            # Obsidian/Qdrant ✅
  └── utils/
      ├── __init__.py ✅
      ├── config.py              # 설정 관리 ✅
      ├── retry.py               # 재시도 로직 ✅
      ├── logger.py              # 로깅 유틸리티 ✅
      ├── monitoring.py          # 모니터링 ✅
      ├── storage.py             # 상태 저장 (Gist) ✅
      └── settings.py            # 사용자 설정 ✅
  ```

- [x] **requirements.txt 작성** ✅
  ```
  python-telegram-bot>=20.0
  google-generativeai>=0.3.0
  requests>=2.31.0
  python-dotenv>=1.0.0
  feedparser>=6.0.0
  ```

- [x] **.env.example 작성** ✅
- [x] **테스트 스크립트 작성** ✅
  - `test_basic.py`: 기본 모듈 테스트 ✅
  - `test_functional.py`: 기능 테스트 ✅
- [x] **가상환경 설정** ✅
  - venv 생성 및 패키지 설치 완료 ✅

### 1.3 Telegram Bot 기본

- [ ] **Bot 생성**
  - @BotFather로 봇 생성
  - Token 발급
  - 기본 명령어 설정 (/start, /help)

- [x] **Telegram 전송 모듈 구현** ✅
  - `src/bot/telegram.py`: 메시지 전송 함수 ✅
  - `src/bot/messages.py`: 메시지 포맷팅 유틸 ✅

### 1.4 날씨 기능 (Week 1)

- [x] **OpenWeatherMap 연동** ✅
  - API Key 발급 (사용자 작업 필요)
  - 위치 설정 (서울) ✅
  - 응답 파싱 ✅
  - 웹 fallback 구현 ✅ (API 키 없을 때 wttr.in 사용)

- [x] **날씨 메시지 생성** ✅
  - 기온, 체감온도 ✅
  - 강수확률 ✅
  - 옷차림 추천 로직 ✅
  - 우산 필요 여부 ✅

- [x] **Gemini 연동** ✅
  - API Key 발급 (사용자 작업 필요)
  - 프롬프트 템플릿 ✅
  - 자연스러운 문장 생성 ✅

- [x] **첫 Workflow 테스트** ✅
  - `morning-weather.yml` 작성 ✅
  - `python src/main.py weather` 실행 (로컬 테스트 가능)
  - 수동 테스트 (workflow_dispatch) - GitHub Secrets 설정 후 가능

### 1.5 뉴스 기능 (Week 2)

- [x] **뉴스 소스 결정** ✅
  - News API (무료 100/일) ✅
  - Google News RSS (백업) ✅

- [x] **관심사 설정** ✅
  - AI/ML ✅
  - Tech Industry ✅
  - EdTech ✅

- [x] **요약 파이프라인** ✅
  - 뉴스 수집 → Gemini 요약 → Telegram 전송 ✅

- [x] **뉴스 Workflow 구현** ✅
  - `morning-news.yml` 작성 ✅
  - 테스트 및 검증 (GitHub Secrets 설정 후 가능)

---

## Phase 2: Core Features (Week 3-5)

### 2.1 Google Calendar 연동

- [ ] **OAuth 설정** (사용자 작업 필요)
  - Google Cloud Console 프로젝트
  - Calendar API 활성화
  - OAuth 2.0 자격 증명
  - Refresh Token 발급

- [x] **일정 조회 기능** ✅
  - 오늘 일정 ✅
  - 내일 일정 ✅
  - 특정 기간 일정 ✅

- [x] **일정 브리핑 메시지** ✅
  - 시간순 정렬 ✅
  - 중요 일정 강조 ✅
  - Gemini로 자연스러운 문장 생성 ✅

- [x] **일정 Workflow 구현** ✅
  - `work-schedule.yml` 작성 ✅
  - 평일만 실행 (월-금) ✅

### 2.2 Gmail 연동 (선택)

- [ ] **Gmail API 설정**
  - 읽기 권한
  - 라벨 기반 필터링

- [ ] **이메일 요약**
  - 제목, 발신자, 간단 요약
  - 중요도 분류

### 2.3 퇴근/저녁 기능

- [x] **퇴근 알림** ✅
  - 저녁 일정 확인 ✅
  - 퇴근길 콘텐츠 추천 ✅

- [ ] **영화/유튜브 추천** (향후 개선)
  - YouTube Data API
  - TMDB API
  - 트렌드 기반

- [x] **퇴근 Workflow 구현** ✅
  - `evening-reminder.yml` 작성 ✅
  - 평일만 실행 ✅

### 2.4 Obsidian/Qdrant 연동

- [x] **프로젝트 정보 검색** ✅
  - Qdrant API 호출 (기본 구조) ✅
  - 또는 Obsidian 파일 직접 읽기 ✅

- [x] **리마인더 생성** ✅
  - 진행 중인 프로젝트 목록 ✅
  - 다음 액션 제안 ✅

- [x] **저녁 프로젝트 Workflow** ✅
  - `night-project.yml` 작성 ✅

---

## Phase 3: Enhancement (Week 6-7)

### 3.1 이미지 생성 (선택)

- [ ] **이미지 모델 선택**
  - Flux (무료 티어 확인)
  - DALL-E 3 (유료)
  - Stable Diffusion API

- [ ] **상황별 이미지**
  - 날씨 컨셉 이미지
  - 뉴스 썸네일
  - 인사 이미지

### 3.2 대화형 기능 강화

- [x] **명령어 확장** ✅
  - /weather - 현재 날씨 ✅
  - /news [topic] - 특정 뉴스 ✅
  - /schedule - 일정 조회 ✅
  - /project - 프로젝트 현황 ✅
  - /settings - 설정 확인 ✅
  - /start, /help - 도움말 ✅

- [x] **Polling 방식 구현** ✅
  - 5초마다 새 메시지 확인 ✅
  - 명령어 핸들러 구현 ✅

### 3.3 사용자 설정

- [x] **설정 저장소** ✅
  - GitHub Gist 활용 ✅
  - JSON 형식 ✅

- [x] **설정 항목** ✅
  - 알림 시간 커스터마이징 ✅
  - 관심 뉴스 카테고리 ✅
  - 위치 설정 ✅
  - 알림 on/off ✅

### 3.4 안정화

- [x] **에러 핸들링** ✅
  - API 실패 대응 ✅
  - 재시도 로직 ✅
  - 알림 발송 실패 처리 ✅

- [x] **로깅** ✅
  - 실행 로그 ✅
  - 에러 로그 ✅
  - 사용량 추적 ✅

- [x] **모니터링** ✅
  - 헬스체크 ✅
  - 알림 (Telegram 자체로) ✅

---

## ✅ 우선순위 정리 (즉시 진행)

### 이번 주 (Week 1)
1. [ ] Telegram Bot 생성 (@BotFather) - 사용자 작업 필요
2. [ ] Gemini API Key 발급 - 사용자 작업 필요
3. [ ] OpenWeatherMap API Key 발급 - 사용자 작업 필요
4. [x] GitHub Repository 생성 ✅ (이미 존재)
5. [x] 기본 프로젝트 구조 생성 ✅
6. [x] 첫 Workflow (날씨 알림) 구현 ✅

### 다음 주 (Week 2)
7. [x] 뉴스 브리핑 Workflow ✅
8. [x] Google Calendar 연동 준비 ✅
9. [x] 일정 브리핑 Workflow ✅

---

## 🔧 기술 노트

### 환경변수 목록

```bash
# Telegram
TELEGRAM_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx

# LLM
GEMINI_API_KEY=xxx

# Weather
OPENWEATHER_API_KEY=xxx

# Google APIs
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REFRESH_TOKEN=xxx

# Optional
NEWS_API_KEY=xxx
YOUTUBE_API_KEY=xxx
GIST_TOKEN=xxx

# Qdrant/Obsidian (Optional)
QDRANT_URL=xxx
QDRANT_API_KEY=xxx
OBSIDIAN_VAULT_PATH=xxx
```

### 빠른 시작

```bash
# 1. Repository 생성
gh repo create proactive-ai-bot --public
cd proactive-ai-bot

# 2. 기본 구조 생성
mkdir -p .github/workflows src/{bot,services,utils}
touch src/__init__.py src/main.py requirements.txt

# 3. Secrets 설정
gh secret set TELEGRAM_TOKEN
gh secret set TELEGRAM_CHAT_ID
gh secret set GEMINI_API_KEY
gh secret set OPENWEATHER_API_KEY

# 4. 첫 Workflow 테스트
gh workflow run morning-weather.yml
```

---

## 📝 회의록/결정사항

### 2025-12-03: 프로젝트 시작
- 프로젝트 구조 결정
- GitHub Actions 기반으로 결정
- Gemini Flash 메인 LLM으로 결정
- Phase 1 MVP 2주 목표

### 2025-12-03: GitHub Actions 전환
- Oracle Cloud → GitHub Actions 변경
- n8n 제거 → Python 직접 구현
- 상태 저장: GitHub Gist 활용

---
*Last Updated: 2025-12-04*

