# PRD - Proactive AI Telegram Bot

## 1. 프로젝트 개요

### 1.1 배경
현재 AI 서비스들은 **반응형(Reactive)** - 사용자가 물어봐야 답한다.
이 프로젝트는 **능동형(Proactive)** - AI가 먼저 필요한 정보를 제공한다.

### 1.2 목표
- 시간대별 맞춤 정보 자동 제공
- Telegram을 통한 편리한 소통
- 최소 비용으로 24시간 운영 ($0 목표)

### 1.3 성공 지표
- 일일 활성 메시지: 5회 이상 (AI→사용자)
- 정보 유용성: 체감 만족도 80%+
- 월 운영 비용: $0 (무료 티어 최대 활용)

---

## 2. 타임라인별 기능 상세

### 2.1 🌅 아침 (07:00 KST)

| 기능 | 상세 | 데이터 소스 |
|------|------|-------------|
| 날씨 브리핑 | 현재 기온, 체감온도, 강수확률 | OpenWeatherMap API |
| 옷차림 추천 | 기온별 추천 (따뜻하게/시원하게) | 날씨 데이터 기반 규칙 |
| 우산 알림 | 강수확률 30% 이상시 알림 | 날씨 데이터 |
| 자연스러운 문장 | Gemini로 친근한 메시지 생성 | Gemini 1.5 Flash |

**예시 메시지:**
```
🌤 좋은 아침이에요!

오늘 서울 날씨:
- 현재 5°C (체감 2°C)
- 최고 12°C / 최저 3°C
- 강수확률 10%

👔 추천: 따뜻한 겉옷 필수! 낮에는 조금 풀리니 레이어드 추천
☂️ 우산은 필요 없어요
```

### 2.2 🚇 출근길 (08:00 KST)

| 기능 | 상세 | 데이터 소스 |
|------|------|-------------|
| 뉴스 브리핑 | 관심 분야 3-5개 기사 요약 | News API, Google News RSS |
| 출처 제공 | 원문 링크 포함 | - |
| 카테고리 | AI/Tech, 업계 동향, 일반 | 사용자 설정 |

**예시 메시지:**
```
📰 오늘의 테크 뉴스

1️⃣ [AI] Claude 4.5 출시, 코딩 능력 대폭 향상
   "Anthropic이 최신 모델 공개..."
   🔗 techcrunch.com/...

2️⃣ [Tech] 애플, M5 칩 개발 본격화
   "2026년 출시 목표로..."
   🔗 macrumors.com/...

3️⃣ [Industry] 에듀테크 시장 2025년 전망
   "AI 기반 학습의 성장..."
   🔗 edtechreview.com/...
```

### 2.3 🏢 출근 후 (09:30 KST, 평일만)

| 기능 | 상세 | 데이터 소스 |
|------|------|-------------|
| 일정 브리핑 | 오늘 일정 정리 | Google Calendar |
| 이메일 요약 | 중요 이메일 하이라이트 | Gmail API (선택) |
| 토픽 분석 | 요청시 특정 주제 리서치 | 웹 검색 + LLM 분석 |

**예시 메시지:**
```
📅 오늘 일정 브리핑

09:00 - 현재 시각
10:00 - 팀 스탠드업 (Zoom)
14:00 - AI 프로젝트 리뷰
16:00 - 1:1 미팅 (김팀장)

📧 확인 필요한 메일: 3건
- [긴급] 서버 점검 안내
- [회신요망] Q4 예산 검토
- [FYI] 신규 입사자 안내
```

### 2.4 🚶 퇴근시간 (18:00 KST, 평일만)

| 기능 | 상세 | 데이터 소스 |
|------|------|-------------|
| 저녁 일정 | 오늘 저녁/내일 주요 일정 | Google Calendar |
| 퇴근길 콘텐츠 | 읽을거리/볼거리 추천 | 웹 검색 |
| 트렌드 | 요즘 유행 영화/유튜브 | YouTube API, TMDB API |

### 2.5 🏠 저녁 (21:00 KST)

| 기능 | 상세 | 데이터 소스 |
|------|------|-------------|
| 프로젝트 리마인드 | 진행 중인 개인 프로젝트 | Obsidian, Qdrant |
| 콘텐츠 추천 | 영화, 유튜브, 글 | 웹 검색 |
| 내일 프리뷰 | 내일 주요 일정 미리보기 | Google Calendar |

---

## 3. 기술 아키텍처

### 3.1 아키텍처 개요

**GitHub Actions 기반 서버리스 아키텍처**

```
GitHub Actions (Cron Scheduler)
    ↓
Python Script (main.py)
    ↓
┌──────────┬──────────┬──────────┐
│ Gemini   │ Weather  │ Telegram │
│ News     │ Calendar │ Bot API  │
│ Projects │          │          │
└──────────┴──────────┴──────────┘
```

### 3.2 핵심 기술 스택

| 구성요소 | 기술 | 비고 |
|---------|------|------|
| 스케줄링 | GitHub Actions Cron | 무료 (월 2,000분) |
| 실행 환경 | Python 3.11 | GitHub Actions Runner |
| LLM | Gemini 1.5 Flash | 무료 (1500 RPD) |
| 메시지 전송 | python-telegram-bot | Telegram Bot API |
| 상태 저장 | GitHub Gist | 간단한 JSON 저장 |

### 3.3 Workflow 스케줄

| 기능 | KST | UTC | Cron Expression |
|------|-----|-----|-----------------|
| 아침 날씨 | 07:00 | 22:00 (전날) | `0 22 * * *` |
| 출근길 뉴스 | 08:00 | 23:00 (전날) | `0 23 * * *` |
| 일정 브리핑 | 09:30 | 00:30 | `30 0 * * 1-5` |
| 퇴근 알림 | 18:00 | 09:00 | `0 9 * * 1-5` |
| 저녁 프로젝트 | 21:00 | 12:00 | `0 12 * * *` |

### 3.4 LLM 선택

| 모델 | 비용 | 무료 티어 | 권장 용도 |
|------|------|-----------|-----------|
| **Gemini 1.5 Flash** | $0 | 15 RPM, 1500 RPD | ✅ 메인 (뉴스 요약, 분석) |
| Gemini 1.5 Pro | $0 | 2 RPM, 50 RPD | 복잡한 분석 |
| GPT-4o-mini | $0.15/1M | - | 고품질 필요시 |

**권장: Gemini 1.5 Flash 시작, 필요시 Pro 혼용**

---

## 4. API 및 서비스 목록

### 필수 API Keys

| 서비스 | 용도 | 무료 티어 |
|--------|------|-----------|
| Telegram Bot | 메시지 전송 | 무제한 |
| Gemini API | LLM | 1500 요청/일 |
| OpenWeatherMap | 날씨 | 1000 요청/일 |
| Google Calendar | 일정 | 무제한 |

### 선택 API Keys

| 서비스 | 용도 | 비고 |
|--------|------|------|
| News API | 뉴스 검색 | 100 요청/일 무료 |
| YouTube Data API | 영상 추천 | 10000 단위/일 |
| TMDB API | 영화 정보 | 무료 |
| Gmail API | 이메일 요약 | OAuth 필요 |

---

## 5. 개발 로드맵

### Phase 1: MVP (2주)
- GitHub Actions 셋업
- Telegram Bot 기본 설정
- 아침 날씨 알림 구현
- 출근길 뉴스 브리핑 구현

### Phase 2: Core Features (3주)
- Google Calendar 연동
- 출근 후 일정 브리핑
- 퇴근/저녁 알림 구현
- Obsidian/Qdrant 연동

### Phase 3: Enhancement (2주)
- 이미지 생성 연동 (선택)
- 대화형 인터랙션 강화
- 사용자 설정 커스터마이징
- 안정화 및 최적화

---

## 6. 리스크 및 대응

| 리스크 | 가능성 | 영향 | 대응 |
|--------|--------|------|------|
| GitHub Actions 한도 초과 | 저 | 중 | 일일 4분 이하로 제한 |
| Gemini API 한도 초과 | 저 | 중 | 캐싱 + 요청 최적화 |
| Workflow 실행 실패 | 중 | 중 | 에러 핸들링 + 재시도 |
| Calendar 권한 이슈 | 중 | 고 | OAuth 사전 테스트 |

---

## 7. 참고 자료

- [Architecture - Proactive AI Telegram Bot](./Architecture%20-%20Proactive%20AI%20Telegram%20B.md)
- [Development Tasks](./TASKS.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [python-telegram-bot](https://python-telegram-bot.org/)
- [Gemini API](https://ai.google.dev/)

---

## 📝 변경 이력

| 날짜 | 내용 |
|------|------|
| 2025-12-03 | Oracle Cloud → GitHub Actions 전환 결정 |
| 2025-12-03 | PRD 문서 작성 |

---
*Last Updated: 2025-12-03*

