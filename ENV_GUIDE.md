# 환경변수 가이드

## 필수 vs 선택 환경변수

### ✅ 필수 환경변수 (반드시 설정 필요)

이 값들이 없으면 해당 기능이 작동하지 않습니다:

| 환경변수 | 용도 | 없을 때 동작 |
|---------|------|------------|
| `TELEGRAM_TOKEN` | Telegram 메시지 전송 | ❌ 메시지 전송 실패 |
| `TELEGRAM_CHAT_ID` | 메시지를 보낼 채팅방 ID | ❌ 메시지 전송 실패 |
| `GEMINI_API_KEY` | LLM 메시지 생성 | ⚠️ LLM 없이 기본 포맷만 사용 |

### 🔶 기능별 필수 환경변수

각 명령어를 실행하려면 해당 API 키가 필요합니다:

#### `python src/main.py weather`
- **필수**: `OPENWEATHER_API_KEY`
- 없을 때: ❌ 날씨 데이터를 가져올 수 없음

#### `python src/main.py news`
- **선택**: `NEWS_API_KEY`
- 없을 때: ✅ Google News RSS로 자동 fallback

#### `python src/main.py schedule`
- **필수**: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`
- 없을 때: ❌ 일정을 가져올 수 없음 (빈 일정 메시지 전송)

#### `python src/main.py evening`
- **선택**: Google Calendar API (일정 확인용)
- 없을 때: ⚠️ 일정 없이 콘텐츠 추천만 표시

#### `python src/main.py night`
- **선택**: `QDRANT_URL`, `QDRANT_API_KEY` 또는 `OBSIDIAN_VAULT_PATH`
- 없을 때: ✅ 플레이스홀더 메시지 전송

### 🔹 선택 환경변수 (없어도 동작)

| 환경변수 | 용도 | 없을 때 동작 |
|---------|------|------------|
| `NEWS_API_KEY` | News API 사용 | ✅ Google News RSS 사용 |
| `GIST_TOKEN` | 상태 저장 | ⚠️ 상태 저장 불가 (기능 제한) |
| `QDRANT_URL`, `QDRANT_API_KEY` | 프로젝트 검색 | ✅ Obsidian 또는 플레이스홀더 사용 |
| `OBSIDIAN_VAULT_PATH` | Obsidian 연동 | ⚠️ 프로젝트 리마인더 제한적 |
| `YOUTUBE_API_KEY` | YouTube 추천 | ⚠️ 콘텐츠 추천 제한적 |

## 동작 방식

### Graceful Degradation (우아한 성능 저하)

코드는 대부분의 경우 API 키가 없어도:
1. ⚠️ 경고 로그만 출력
2. ✅ 가능한 대안 사용 (예: RSS fallback)
3. ✅ 기본 메시지라도 전송

### 예외 처리

- **Telegram 전송**: 토큰이 없으면 완전 실패
- **날씨 기능**: API 키 없으면 None 반환 → 명령어 실패
- **일정 기능**: OAuth 없으면 빈 일정 메시지 전송

## 권장 설정 순서

### 최소 설정 (기본 기능 테스트)
```bash
TELEGRAM_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
GEMINI_API_KEY=xxx
OPENWEATHER_API_KEY=xxx
```

### 권장 설정 (모든 기능 사용)
```bash
# 위의 최소 설정 +
NEWS_API_KEY=xxx  # RSS보다 품질 좋음
GIST_TOKEN=xxx     # 설정 저장 가능
```

### 완전한 설정 (모든 기능)
```bash
# 위의 권장 설정 +
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REFRESH_TOKEN=xxx  # 일정 기능
QDRANT_URL=xxx            # 프로젝트 검색
OBSIDIAN_VAULT_PATH=xxx   # 또는 Obsidian 사용
```

## 테스트 방법

```bash
# 1. 헬스체크 (어떤 키가 설정되었는지 확인)
PYTHONPATH=. python3 src/main.py health

# 2. 각 기능별 테스트
PYTHONPATH=. python3 src/main.py weather   # OPENWEATHER_API_KEY 필요
PYTHONPATH=. python3 src/main.py news     # NEWS_API_KEY 없어도 RSS 사용
PYTHONPATH=. python3 src/main.py schedule # Google APIs 필요
```

---
*Last Updated: 2025-12-04*

