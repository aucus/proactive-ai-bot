# Development Tasks - Proactive AI Telegram Bot

## 📊 Progress Overview

| Phase | 상태 | 진행률 | 기간 |
|-------|------|--------|------|
| Phase 1: MVP | ⏳ 대기 | 0% | 2주 |
| Phase 2: Core | ⏳ 대기 | 0% | 3주 |
| Phase 3: Enhancement | ⏳ 대기 | 0% | 2주 |

---

## Phase 1: MVP (Week 1-2)

### 1.1 인프라 셋업

- [ ] **Oracle Cloud 인스턴스 확보**
  - Priority: 🔴 Critical
  - 리전: ap-chuncheon-1 또는 대안
  - 스펙: A1.Flex (1 OCPU, 6GB RAM 시작)
  - 기존 스크립트 활용

- [ ] **Docker 환경 구성**
  - docker-compose.yml 작성
  - n8n 컨테이너
  - Telegram Bot 컨테이너
  - (선택) Qdrant 컨테이너

- [ ] **도메인/SSL 설정**
  - Cloudflare DNS 연동
  - Let's Encrypt 인증서
  - Webhook URL 확보

### 1.2 Telegram Bot 기본

- [ ] **Bot 생성**
  - @BotFather로 봇 생성
  - Token 발급
  - 기본 명령어 설정 (/start, /help, /settings)

- [ ] **Bot 코드 작성**
  ```python
  # 기본 구조
  - handlers/
    - start.py
    - weather.py
    - news.py
    - schedule.py
  - services/
    - llm.py (Gemini)
    - weather.py
    - calendar.py
  - main.py
  ```

- [ ] **Webhook 모드 설정**
  - n8n Webhook 또는 직접 서버

### 1.3 n8n 워크플로우

- [ ] **n8n 설치**
  - Docker로 설치
  - 환경변수 설정
  - 기본 인증 설정

- [ ] **Cron 워크플로우 생성**
  | 이름 | 시간 | 기능 |
  |------|------|------|
  | morning_weather | 07:00 | 날씨 알림 |
  | morning_news | 08:00 | 뉴스 브리핑 |
  | work_schedule | 09:30 | 일정 브리핑 |
  | evening_reminder | 18:00 | 퇴근 알림 |
  | night_project | 21:00 | 프로젝트 리마인드 |

### 1.4 날씨 기능 (Week 2)

- [ ] **OpenWeatherMap 연동**
  - API Key 발급
  - 위치 설정 (서울)
  - 응답 파싱

- [ ] **날씨 메시지 생성**
  - 기온, 체감온도
  - 강수확률
  - 옷차림 추천 로직
  - 우산 필요 여부

- [ ] **Gemini 연동**
  - API Key 발급
  - 프롬프트 템플릿
  - 자연스러운 문장 생성

### 1.5 뉴스 기능 (Week 2)

- [ ] **뉴스 소스 결정**
  - News API (무료 100/일)
  - Google News RSS
  - 직접 크롤링 (백업)

- [ ] **관심사 설정**
  - AI/ML
  - Tech Industry
  - EdTech

- [ ] **요약 파이프라인**
  - 뉴스 수집 → Gemini 요약 → Telegram 전송

---

## Phase 2: Core Features (Week 3-5)

### 2.1 Google Calendar 연동

- [ ] **OAuth 설정**
  - Google Cloud Console 프로젝트
  - Calendar API 활성화
  - OAuth 2.0 자격 증명

- [ ] **일정 조회 기능**
  - 오늘 일정
  - 내일 일정
  - 특정 기간 일정

- [ ] **n8n Google Calendar 노드**
  - 또는 Python googleapis 직접 사용

### 2.2 Gmail 연동 (선택: Outlook)

- [ ] **Gmail API 설정**
  - 읽기 권한
  - 라벨 기반 필터링

- [ ] **이메일 요약**
  - 제목, 발신자, 간단 요약
  - 중요도 분류

### 2.3 회사 Outlook 연동 (옵션)

- [ ] **Microsoft Graph API**
  - 회사 정책 확인 필요
  - Azure AD 앱 등록

### 2.4 퇴근/저녁 기능

- [ ] **퇴근 알림**
  - 저녁 일정 확인
  - 퇴근길 콘텐츠 추천

- [ ] **영화/유튜브 추천**
  - YouTube Data API
  - TMDB API
  - 트렌드 기반

### 2.5 Obsidian/Qdrant 연동

- [ ] **프로젝트 정보 검색**
  - Qdrant API 호출
  - 또는 Obsidian 파일 직접 읽기

- [ ] **리마인더 생성**
  - 진행 중인 프로젝트 목록
  - 다음 액션 제안

---

## Phase 3: Enhancement (Week 6-7)

### 3.1 이미지 생성

- [ ] **이미지 모델 선택**
  - Flux (무료 티어 확인)
  - DALL-E 3 (유료)
  - Stable Diffusion API

- [ ] **상황별 이미지**
  - 날씨 컨셉 이미지
  - 뉴스 썸네일
  - 인사 이미지

### 3.2 대화형 기능 강화

- [ ] **명령어 확장**
  - /weather - 현재 날씨
  - /news [topic] - 특정 뉴스
  - /schedule - 일정 조회
  - /project - 프로젝트 현황
  - /settings - 설정 변경

- [ ] **자연어 처리**
  - "오늘 날씨 어때?" → 날씨 응답
  - "내일 일정 알려줘" → 캘린더 조회

### 3.3 사용자 설정

- [ ] **설정 저장소**
  - JSON 파일 또는
  - SQLite 또는
  - Qdrant metadata

- [ ] **설정 항목**
  - 알림 시간 커스터마이징
  - 관심 뉴스 카테고리
  - 위치 설정
  - 알림 on/off

### 3.4 안정화

- [ ] **에러 핸들링**
  - API 실패 대응
  - 재시도 로직
  - 알림 발송 실패 처리

- [ ] **로깅**
  - 실행 로그
  - 에러 로그
  - 사용량 추적

- [ ] **모니터링**
  - 헬스체크
  - 알림 (Telegram 자체로)

---

## 🔧 기술 노트

### Docker Compose 예시

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
    volumes:
      - n8n_data:/home/node/.n8n

  bot:
    build: ./telegram-bot
    restart: always
    environment:
      - TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - n8n

volumes:
  n8n_data:
```

### 환경변수 목록

```bash
# Telegram
TELEGRAM_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx  # 자신의 chat_id

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
```

---

## 📝 회의록/결정사항

### 2025-12-03: 프로젝트 시작
- 프로젝트 구조 결정
- Oracle Cloud 우선 사용
- Gemini Flash 메인 LLM으로 결정
- Phase 1 MVP 2주 목표

---
*Last Updated: 2025-12-03*


---

## 📝 2025-12-03 업데이트: GitHub Actions 전환

> ⚠️ Oracle Cloud → GitHub Actions 변경으로 인한 태스크 수정

### Phase 1 수정사항

#### ~~1.1 인프라 셋업~~ → 1.1 GitHub Actions 셋업

- [ ] **Repository 생성**
  - Priority: 🔴 Critical
  - `proactive-ai-bot` (Public)
  - GitHub Actions 활성화

- [ ] **Workflow 파일 생성**
  ```
  .github/workflows/
  ├── morning-weather.yml    # 07:00 KST (cron: 0 22 * * *)
  ├── morning-news.yml       # 08:00 KST (cron: 0 23 * * *)
  ├── work-schedule.yml      # 09:30 KST (cron: 30 0 * * 1-5)
  ├── evening-reminder.yml   # 18:00 KST (cron: 0 9 * * 1-5)
  └── night-project.yml      # 21:00 KST (cron: 0 12 * * *)
  ```

- [ ] **Secrets 설정**
  - TELEGRAM_TOKEN
  - TELEGRAM_CHAT_ID  
  - GEMINI_API_KEY
  - OPENWEATHER_API_KEY

#### ~~1.3 n8n 워크플로우~~ → 삭제 (Python 직접 구현)

### 새로운 태스크 추가

- [ ] **Python 프로젝트 구조**
  ```
  src/
  ├── main.py          # CLI 엔트리포인트
  ├── bot/telegram.py  # 메시지 전송
  ├── services/
  │   ├── weather.py
  │   ├── news.py
  │   ├── llm.py       # Gemini
  │   └── calendar.py
  └── utils/config.py
  ```

- [ ] **requirements.txt**
  ```
  python-telegram-bot>=20.0
  google-generativeai
  requests
  python-dotenv
  ```

### 수정된 빠른 시작

```bash
# 1. Repository 생성
gh repo create proactive-ai-bot --public
cd proactive-ai-bot

# 2. 기본 구조 생성
mkdir -p .github/workflows src/{bot,services,utils}

# 3. Secrets 설정
gh secret set TELEGRAM_TOKEN
gh secret set TELEGRAM_CHAT_ID
gh secret set GEMINI_API_KEY
gh secret set OPENWEATHER_API_KEY

# 4. 첫 Workflow 테스트
gh workflow run morning-weather.yml
```

---

## ✅ 우선순위 정리 (GitHub Actions 기준)

### 즉시 진행 (이번 주)
1. [ ] Telegram Bot 생성 (@BotFather)
2. [ ] Gemini API Key 발급
3. [ ] OpenWeatherMap API Key 발급
4. [ ] GitHub Repository 생성
5. [ ] 첫 Workflow (날씨 알림) 구현

### 다음 주
6. [ ] 뉴스 브리핑 Workflow
7. [ ] Google Calendar 연동
8. [ ] 일정 브리핑 Workflow

---
*Last Updated: 2025-12-03 (GitHub Actions 전환)*
