# Architecture - Proactive AI Telegram Bot (GitHub Actions)

## 🏗️ 아키텍처 개요

Oracle Cloud 대신 **GitHub Actions**를 활용한 서버리스 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                 GitHub Actions                       │
│            (Cron Scheduler + Runner)                │
│                                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ 07:00   │ │ 08:00   │ │ 09:30   │ │ 18:00   │   │
│  │ Weather │ │ News    │ │ Schedule│ │ Evening │   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │
│       │          │          │          │          │
│       └──────────┴──────────┴──────────┘          │
│                      │                             │
└──────────────────────┼─────────────────────────────┘
                       ▼
              ┌─────────────────┐
              │  Python Script  │
              │  (main.py)      │
              └────────┬────────┘
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Gemini API │  │ Weather    │  │ Telegram   │
│ (LLM)      │  │ Calendar   │  │ Bot API    │
│            │  │ News APIs  │  │            │
└────────────┘  └────────────┘  └────────────┘
```

---

## ✅ GitHub Actions 장점

| 항목 | 내용 |
|------|------|
| 비용 | **완전 무료** (월 2,000분, Public Repo) |
| 관리 | 서버 관리 불필요 |
| 안정성 | GitHub 인프라 활용 |
| 버전관리 | 코드와 스케줄 함께 관리 |
| 시크릿 | GitHub Secrets로 안전하게 저장 |

## ⚠️ 제약사항 및 대응

| 제약 | 영향 | 대응 |
|------|------|------|
| 최소 간격 5분 | 실시간 응답 불가 | 스케줄 기반으로 충분 |
| 시간 부정확 (±수분) | 정확한 시간 보장 안됨 | 아침/저녁 알림이라 OK |
| 상태 저장 없음 | 대화 컨텍스트 유지 어려움 | Gist/Supabase 활용 |
| 월 2,000분 제한 | 과다 사용시 중단 | 1일 30분 미만으로 충분 |

---

## 📁 Repository 구조

```
proactive-ai-bot/
├── .github/
│   └── workflows/
│       ├── morning-weather.yml    # 07:00 KST
│       ├── morning-news.yml       # 08:00 KST
│       ├── work-schedule.yml      # 09:30 KST
│       ├── evening-reminder.yml   # 18:00 KST
│       └── night-project.yml      # 21:00 KST
├── src/
│   ├── __init__.py
│   ├── main.py                    # 메인 엔트리포인트
│   ├── bot/
│   │   ├── telegram.py            # Telegram 전송
│   │   └── messages.py            # 메시지 포맷팅
│   ├── services/
│   │   ├── weather.py             # 날씨 API
│   │   ├── news.py                # 뉴스 수집
│   │   ├── calendar.py            # Google Calendar
│   │   ├── llm.py                 # Gemini API
│   │   └── projects.py            # Obsidian/Qdrant
│   └── utils/
│       ├── config.py              # 설정 관리
│       └── storage.py             # 상태 저장 (Gist)
├── requirements.txt
├── README.md
└── .env.example
```

---

## ⏰ Workflow 스케줄

### KST → UTC 변환
GitHub Actions는 UTC 기준이므로 변환 필요

| 기능 | KST | UTC | Cron Expression |
|------|-----|-----|-----------------|
| 아침 날씨 | 07:00 | 22:00 (전날) | `0 22 * * *` |
| 출근길 뉴스 | 08:00 | 23:00 (전날) | `0 23 * * *` |
| 일정 브리핑 | 09:30 | 00:30 | `30 0 * * 1-5` |
| 퇴근 알림 | 18:00 | 09:00 | `0 9 * * 1-5` |
| 저녁 프로젝트 | 21:00 | 12:00 | `0 12 * * *` |

### 예시 Workflow 파일

```yaml
# .github/workflows/morning-weather.yml
name: Morning Weather

on:
  schedule:
    - cron: '0 22 * * *'  # 07:00 KST
  workflow_dispatch:  # 수동 실행

jobs:
  send-weather:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: pip install -r requirements.txt
        
      - name: Run weather notification
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          OPENWEATHER_API_KEY: ${{ secrets.OPENWEATHER_API_KEY }}
        run: python src/main.py weather
```

---

## 🔐 GitHub Secrets 설정

Repository Settings → Secrets and variables → Actions

| Secret Name | 용도 |
|-------------|------|
| `TELEGRAM_TOKEN` | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | 수신자 Chat ID |
| `GEMINI_API_KEY` | Gemini API Key |
| `OPENWEATHER_API_KEY` | 날씨 API Key |
| `GOOGLE_CREDENTIALS` | Google OAuth JSON (Base64) |
| `GIST_TOKEN` | 상태 저장용 Gist Token |

---

## 💾 상태 저장 옵션

대화 컨텍스트, 설정 등 저장 필요시:

### Option A: GitHub Gist (권장)
```python
# 간단한 JSON 저장소로 활용
import requests

def save_state(data):
    # Gist 업데이트
    pass

def load_state():
    # Gist 읽기
    pass
```

### Option B: Supabase Free
- PostgreSQL 500MB 무료
- REST API 제공
- 더 복잡한 상태 관리 가능

### Option C: Repository 파일
- JSON 파일로 저장
- 매 실행시 commit (비추천 - 히스토리 오염)

---

## 🔄 대화형 기능 구현

GitHub Actions는 Webhook 수신 불가 → 대안 필요

### Option A: Polling 방식
```yaml
# 5분마다 새 메시지 확인
on:
  schedule:
    - cron: '*/5 * * * *'
```
- 장점: 구현 간단
- 단점: 5분 지연, 분 사용량 증가

### Option B: Cloudflare Workers (하이브리드)
```
Telegram Webhook → Cloudflare Worker → (즉시 응답)
                                      ↓
                              GitHub Actions (복잡한 작업)
```
- 장점: 즉시 응답 가능
- 단점: 두 시스템 관리

### Option C: 단방향 알림만 (MVP)
- 봇이 먼저 알림만 보냄
- 사용자 명령은 Phase 2에서 고려
- **MVP로 권장**

---

## 📊 예상 사용량

### 일일 실행 시간
| Workflow | 횟수 | 예상 시간 | 합계 |
|----------|------|-----------|------|
| Weather | 1회 | 30초 | 0.5분 |
| News | 1회 | 60초 | 1분 |
| Schedule | 1회 | 45초 | 0.75분 |
| Evening | 1회 | 30초 | 0.5분 |
| Night | 1회 | 45초 | 0.75분 |
| **합계** | 5회 | - | **~4분/일** |

### 월간 사용량
- 일일: ~4분
- 월간: ~120분
- 무료 한도: 2,000분
- **여유: 충분** ✅

---

## 🚀 빠른 시작 가이드

### Step 1: Repository 생성
```bash
gh repo create proactive-ai-bot --public
cd proactive-ai-bot
```

### Step 2: 기본 구조 생성
```bash
mkdir -p .github/workflows src/{bot,services,utils}
touch src/__init__.py src/main.py requirements.txt
```

### Step 3: Secrets 설정
```bash
# GitHub CLI로 설정
gh secret set TELEGRAM_TOKEN
gh secret set TELEGRAM_CHAT_ID
gh secret set GEMINI_API_KEY
gh secret set OPENWEATHER_API_KEY
```

### Step 4: 첫 Workflow 작성 & 테스트
```bash
# workflow_dispatch로 수동 테스트
gh workflow run morning-weather.yml
```

---

## 📝 변경 이력

| 날짜 | 내용 |
|------|------|
| 2025-12-03 | Oracle Cloud → GitHub Actions 전환 결정 |
| 2025-12-03 | 아키텍처 문서 작성 |

---
*Last Updated: 2025-12-03*
