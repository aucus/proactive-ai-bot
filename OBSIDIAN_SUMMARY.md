# Proactive AI Telegram Bot - 프로젝트 요약

## 📋 프로젝트 개요

**Proactive AI Telegram Bot**은 능동적으로 정보를 제공하는 개인 AI 비서입니다. 사용자가 물어보기 전에 필요한 정보를 시간대별로 자동으로 알려주는 서비스입니다.

### 핵심 컨셉
- **능동형(Proactive)**: AI가 먼저 필요한 정보 제공
- **시간대별 맞춤**: 아침, 출근길, 출근 후, 퇴근, 저녁 시간대별 정보
- **무료 운영**: GitHub Actions + 무료 API 티어 활용 ($0 목표)

---

## 🎯 주요 기능

### 1. 출근 준비 알림 (06:20 KST)
- 집(경기도 남양주)과 회사(서울 신도림) 날씨 동시 제공
- 출발 전 날씨 확인으로 준비물 체크
- 우산 필요 여부 자동 판단

### 2. 뉴스 브리핑 (07:30 KST)
- 관심 분야 뉴스 요약 (AI, Tech, EdTech)
- News API 또는 Google News RSS 사용
- Gemini로 자연스러운 요약 생성

### 3. 일정 브리핑 (09:30 KST, 평일)
- Google Calendar 연동
- 오늘 일정 시간순 정렬
- 중요 일정 자동 강조

### 4. 퇴근 알림 (17:30 KST, 평일)
- 저녁 일정 확인
- 내일 주요 일정 미리보기
- 퇴근길 콘텐츠 추천 (향후 확장)

### 5. 프로젝트 리마인더 (21:00 KST)
- 진행 중인 프로젝트 목록
- 다음 액션 제안
- Qdrant/Obsidian 연동 (선택)

---

## 🏗️ 기술 스택

### 인프라
- **GitHub Actions**: 서버리스 스케줄링 (무료)
- **Python 3.11**: 메인 언어
- **GitHub Secrets**: 환경변수 관리

### API & 서비스
- **Telegram Bot API**: 메시지 전송
- **Gemini 2.0 Flash**: LLM (자연스러운 메시지 생성)
- **OpenWeatherMap API**: 날씨 정보 (웹 fallback 지원)
- **News API / Google News RSS**: 뉴스 수집
- **Google Calendar API**: 일정 조회
- **wttr.in**: 날씨 웹 fallback (API 키 불필요)

### 주요 라이브러리
- `python-telegram-bot`: Telegram 봇
- `google-generativeai`: Gemini API
- `requests`: HTTP 요청
- `feedparser`: RSS 파싱
- `python-dotenv`: 환경변수 관리

---

## 📁 프로젝트 구조

```
proactive-ai-bot/
├── .github/workflows/          # GitHub Actions 워크플로우
│   ├── commute-weather.yml     # 출근 알림 (06:20 KST)
│   ├── morning-news.yml        # 뉴스 브리핑 (07:30 KST)
│   ├── work-schedule.yml       # 일정 브리핑 (09:30 KST)
│   ├── evening-reminder.yml    # 퇴근 알림 (17:30 KST)
│   └── night-project.yml       # 프로젝트 리마인더 (21:00 KST)
│
├── src/
│   ├── main.py                 # CLI 엔트리포인트
│   ├── bot/
│   │   ├── telegram.py         # Telegram 전송
│   │   ├── messages.py         # 메시지 포맷팅
│   │   ├── handlers.py         # 명령어 핸들러
│   │   └── polling.py          # Polling 서비스
│   ├── services/
│   │   ├── weather.py          # 날씨 서비스
│   │   ├── commute.py          # 출근 날씨 (집+회사)
│   │   ├── news.py             # 뉴스 수집
│   │   ├── calendar.py         # Google Calendar
│   │   ├── evening.py          # 저녁 알림
│   │   ├── projects.py         # 프로젝트 리마인더
│   │   └── llm.py              # Gemini LLM
│   └── utils/
│       ├── config.py           # 환경변수 관리
│       ├── user_config.py      # 사용자 설정 로더
│       ├── storage.py          # GitHub Gist 저장
│       ├── settings.py         # 설정 관리
│       ├── retry.py            # 재시도 로직
│       ├── logger.py           # 로깅
│       └── monitoring.py       # 모니터링
│
├── user_config.json            # 사용자 커스터마이징 설정
├── requirements.txt            # Python 패키지
└── .env                        # 환경변수 (Git에 포함 안됨)
```

---

## ⚙️ 사용자 설정 (user_config.json)

사용자가 시간대와 지역을 커스터마이징할 수 있습니다:

```json
{
  "locations": {
    "home": {
      "city": "Namyangju",
      "country_code": "KR",
      "display_name": "경기도 남양주"
    },
    "office": {
      "city": "Sindorim",
      "country_code": "KR",
      "display_name": "서울 신도림"
    }
  },
  "schedule": {
    "commute": {
      "notification_time": "06:20",
      "enabled": true
    },
    "news": {
      "time": "07:30",
      "enabled": true
    },
    "work_schedule": {
      "time": "09:30",
      "enabled": true
    },
    "evening": {
      "time": "17:30",
      "enabled": true
    },
    "night_project": {
      "time": "21:00",
      "enabled": true
    }
  }
}
```

---

## 🚀 배포 상태

### 완료된 작업
- ✅ GitHub Repository 생성 및 연결
- ✅ 모든 Workflow 파일 생성
- ✅ GitHub Secrets 설정
- ✅ Morning Weather Workflow 테스트 성공
- ✅ 사용자 설정 시스템 구현
- ✅ 출근 알림 기능 (집+회사 날씨)

### 현재 진행률
- Phase 1 (MVP): 60%
- Phase 2 (Core): 70%
- Phase 3 (Enhancement): 80%

---

## 🔧 주요 특징

### 1. Fallback 메커니즘
- 날씨: OpenWeatherMap API → wttr.in 웹 fallback
- 뉴스: News API → Google News RSS fallback
- 모든 선택적 API 키 없이도 기본 기능 동작

### 2. 에러 핸들링
- 재시도 로직 (지수 백오프)
- Graceful degradation
- 상세한 로깅

### 3. 모니터링
- 헬스체크 기능
- 실행 시간 추적
- 사용량 통계

### 4. 확장성
- 사용자 설정 파일로 커스터마이징
- GitHub Gist 기반 상태 저장
- Polling 모드 지원 (대화형)

---

## 📊 실행 스케줄

| 시간 | 기능 | 요일 |
|------|------|------|
| 06:20 KST | 출근 준비 알림 (집+회사 날씨) | 매일 |
| 07:30 KST | 뉴스 브리핑 | 매일 |
| 09:30 KST | 일정 브리핑 | 평일 |
| 17:30 KST | 퇴근 알림 | 평일 |
| 21:00 KST | 프로젝트 리마인더 | 매일 |

---

## 🔐 환경변수

### 필수
- `TELEGRAM_TOKEN`: Telegram Bot 토큰
- `TELEGRAM_CHAT_ID`: Telegram Chat ID
- `GEMINI_API_KEY`: Gemini API 키

### 선택
- `OPENWEATHER_API_KEY`: 날씨 API (없으면 웹 fallback)
- `NEWS_API_KEY`: 뉴스 API (없으면 RSS)
- `GOOGLE_CLIENT_ID/SECRET/REFRESH_TOKEN`: Calendar 연동
- `GIST_TOKEN`: 상태 저장
- `QDRANT_URL/API_KEY`: 프로젝트 검색
- `OBSIDIAN_VAULT_PATH`: Obsidian 연동

---

## 📝 향후 계획

### Phase 3 남은 작업
- 이미지 생성 기능 (선택)
- 대화형 기능 강화 (Polling 완료, 명령어 확장)
- 사용자 설정 UI (현재 JSON 파일 기반)

### Phase 4 (향후)
- Gmail 연동
- YouTube/TMDB 추천
- 더 많은 커스터마이징 옵션

---

## 🔗 관련 문서

- **README.md**: 빠른 시작 가이드
- **TASKS.md**: 개발 태스크 및 진행 상황
- **PRD.md**: 제품 요구사항 문서
- **SETUP_GITHUB.md**: GitHub 배포 가이드
- **DEPLOYMENT.md**: 배포 가이드

---

## 💡 핵심 아이디어

이 프로젝트의 핵심은 **"사용자가 물어보기 전에 필요한 정보를 제공"**하는 것입니다. 
GitHub Actions를 활용한 서버리스 아키텍처로 무료로 24시간 운영하며, 
사용자의 일상 패턴에 맞춰 자동으로 유용한 정보를 제공합니다.

---

*Last Updated: 2025-12-04*
*Repository: https://github.com/aucus/proactive-ai-bot*

