# GitHub Repository 설정 가이드

## 실제 구동을 위한 체크리스트

### ✅ 완료된 작업
- [x] 코드 구현 완료
- [x] Workflow 파일 생성 완료
- [x] 로컬 테스트 완료
- [x] 가상환경 설정 완료

### 🔴 다음 단계 (필수)

#### 1. Git Repository 초기화
```bash
cd /Users/st/workspace_ai/proactive-ai-bot
git init
git add .
git commit -m "Initial commit: Proactive AI Telegram Bot"
```

#### 2. GitHub Repository 생성 및 연결

**옵션 A: GitHub CLI 사용 (권장)**
```bash
gh repo create proactive-ai-bot --public --source=. --remote=origin
git push -u origin main
```

**옵션 B: 수동 생성**
1. GitHub.com에서 새 Repository 생성 (`proactive-ai-bot`)
2. 다음 명령어 실행:
```bash
git remote add origin https://github.com/YOUR_USERNAME/proactive-ai-bot.git
git branch -M main
git push -u origin main
```

#### 3. GitHub Secrets 설정

Repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

**필수로 설정해야 할 Secrets:**

| Secret 이름 | 설명 | 어디서 얻나요? |
|------------|------|---------------|
| `TELEGRAM_TOKEN` | Telegram Bot 토큰 | @BotFather |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | @userinfobot |
| `GEMINI_API_KEY` | Gemini API 키 | https://aistudio.google.com/ |

**선택적 Secrets (없어도 동작):**
- `OPENWEATHER_API_KEY` - 없으면 웹 fallback 사용
- `NEWS_API_KEY` - 없으면 RSS 사용
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` - Calendar 기능용
- `GIST_TOKEN` - 상태 저장용
- `QDRANT_URL`, `QDRANT_API_KEY` - 프로젝트 리마인더용

#### 4. Workflow 테스트

1. Repository → **Actions** 탭
2. 왼쪽에서 Workflow 선택 (예: "Morning Weather")
3. **Run workflow** 버튼 클릭
4. 실행 결과 확인

#### 5. 자동 실행 확인

Workflow가 다음 시간에 자동 실행됩니다:
- 매일 07:00 KST - 날씨 알림
- 매일 08:00 KST - 뉴스 브리핑
- 평일 09:30 KST - 일정 브리핑
- 평일 18:00 KST - 퇴근 알림
- 매일 21:00 KST - 프로젝트 리마인더

## 빠른 배포 스크립트

```bash
# deploy.sh 실행
chmod +x deploy.sh
./deploy.sh
```

또는 수동으로:

```bash
# 1. Git 초기화
git init
git add .
git commit -m "Initial commit"

# 2. GitHub Repository 생성 (GitHub CLI 필요)
gh repo create proactive-ai-bot --public --source=. --remote=origin

# 3. 푸시
git push -u origin main

# 4. Secrets 설정 (웹에서 수동)
echo "GitHub Repository에서 Secrets를 설정하세요!"
```

## 확인 사항

- [ ] Git repository 초기화 완료
- [ ] GitHub repository 생성 및 연결 완료
- [ ] 필수 Secrets 설정 완료 (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY)
- [ ] Workflow 수동 실행 테스트 성공
- [ ] Telegram에서 메시지 수신 확인

---
*Last Updated: 2025-12-04*

