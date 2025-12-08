# GitHub Secrets 설정 가이드

뉴스 중복 방지 기능을 위한 GitHub Secrets 설정 방법을 단계별로 안내합니다.

## 📋 목차

1. [GIST_TOKEN 설정](#1-gist_token-설정)
2. [NEWS_GIST_ID 설정 (선택)](#2-news_gist_id-설정-선택)
3. [SETTINGS_GIST_ID 설정 (선택)](#3-settings_gist_id-설정-선택)

---

## 1. GIST_TOKEN 설정

**GIST_TOKEN**은 GitHub Gist API에 접근하기 위한 Personal Access Token입니다.

### 1-1. GitHub Personal Access Token 생성

1. **GitHub 로그인**
   - https://github.com 에 로그인

2. **Settings 접근**
   - 우측 상단 프로필 아이콘 클릭
   - **Settings** 클릭

3. **Developer settings 이동**
   - 왼쪽 메뉴 하단 **Developer settings** 클릭
   - 또는 직접 접근: https://github.com/settings/apps

4. **Personal access tokens 생성**
   - 왼쪽 메뉴에서 **Personal access tokens** → **Tokens (classic)** 클릭
   - 또는 직접 접근: https://github.com/settings/tokens

5. **Generate new token**
   - **Generate new token** → **Generate new token (classic)** 클릭

6. **토큰 설정**
   - **Note**: `Proactive AI Bot Gist Access` (설명 입력)
   - **Expiration**: 원하는 만료 기간 선택 (예: 90 days, No expiration)
   - **Select scopes**: 다음 권한 체크
     - ✅ `gist` (Create gists 권한)

7. **토큰 생성**
   - 하단 **Generate token** 버튼 클릭
   - ⚠️ **중요**: 생성된 토큰을 즉시 복사하세요! (다시 볼 수 없습니다)
   - 예: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 1-2. GitHub Secrets에 추가

1. **Repository로 이동**
   - https://github.com/YOUR_USERNAME/proactive-ai-bot
   - 또는 로컬에서: `gh repo view --web`

2. **Settings 탭 클릭**
   - Repository 상단 메뉴에서 **Settings** 클릭

3. **Secrets 메뉴 접근**
   - 왼쪽 메뉴에서 **Secrets and variables** → **Actions** 클릭

4. **New repository secret 생성**
   - **New repository secret** 버튼 클릭

5. **Secret 정보 입력**
   - **Name**: `GIST_TOKEN`
   - **Secret**: 위에서 복사한 Personal Access Token 붙여넣기
   - **Add secret** 버튼 클릭

✅ **완료**: GIST_TOKEN이 설정되었습니다!

---

## 2. NEWS_GIST_ID 설정 (선택)

**NEWS_GIST_ID**는 뉴스 중복 방지를 위한 Gist ID입니다. 설정하지 않아도 자동으로 생성되지만, 수동으로 관리하고 싶다면 설정할 수 있습니다.

### 2-1. 자동 생성 방식 (권장)

**설정하지 않아도 됩니다!**

- 첫 번째 뉴스 브리핑 실행 시 자동으로 Gist가 생성됩니다
- 생성된 Gist ID는 로그에서 확인할 수 있습니다
- 이후 실행 시 자동으로 같은 Gist를 사용합니다

### 2-2. 수동 생성 방식

Gist를 수동으로 생성하고 싶다면:

1. **Gist 생성**
   - https://gist.github.com 접속
   - **Create a new gist** 클릭

2. **Gist 설정**
   - **Filename**: `news_state.json`
   - **Content**: 
     ```json
     {
       "seen_urls": [],
       "last_updated": ""
     }
     ```
   - **Create secret gist** 선택 (비공개)
   - **Create secret gist** 버튼 클릭

3. **Gist ID 확인**
   - 생성된 Gist 페이지 URL에서 ID 확인
   - 예: `https://gist.github.com/USERNAME/abc123def456...`
   - Gist ID는 `abc123def456...` 부분입니다

4. **GitHub Secrets에 추가**
   - Repository → Settings → Secrets and variables → Actions
   - **New repository secret** 클릭
   - **Name**: `NEWS_GIST_ID`
   - **Secret**: Gist ID 붙여넣기
   - **Add secret** 버튼 클릭

✅ **완료**: NEWS_GIST_ID가 설정되었습니다!

---

## 3. SETTINGS_GIST_ID 설정 (선택)

**SETTINGS_GIST_ID**는 사용자 설정을 저장하는 Gist ID입니다. NEWS_GIST_ID가 없을 때 뉴스 상태용으로도 사용됩니다.

### 3-1. 자동 생성 방식 (권장)

**설정하지 않아도 됩니다!**

- 첫 번째 설정 저장 시 자동으로 Gist가 생성됩니다
- 생성된 Gist ID는 로그에서 확인할 수 있습니다

### 3-2. 수동 생성 방식

1. **Gist 생성**
   - https://gist.github.com 접속
   - **Create a new gist** 클릭

2. **Gist 설정**
   - **Filename**: `settings.json`
   - **Content**: 
     ```json
     {
       "notifications": {
         "weather": true,
         "news": true,
         "schedule": true,
         "evening": true,
         "night": true
       },
       "news_categories": ["AI", "Tech", "EdTech"],
       "location": {
         "city": "Seoul",
         "country_code": "KR"
       }
     }
     ```
   - **Create secret gist** 선택 (비공개)
   - **Create secret gist** 버튼 클릭

3. **Gist ID 확인 및 추가**
   - Gist ID 확인 (URL에서)
   - GitHub Secrets에 추가
     - **Name**: `SETTINGS_GIST_ID`
     - **Secret**: Gist ID

✅ **완료**: SETTINGS_GIST_ID가 설정되었습니다!

---

## 🔍 설정 확인 방법

### 방법 1: GitHub Actions 로그 확인

1. Repository → **Actions** 탭
2. 최근 실행된 Workflow 클릭
3. **send-news** job 클릭
4. 로그에서 다음 메시지 확인:
   - `Created Gist: abc123...` (자동 생성된 경우)
   - `Loaded state from Gist: abc123...` (기존 Gist 사용)

### 방법 2: 로컬 테스트

```bash
# 환경변수 설정
export GIST_TOKEN="ghp_xxxxxxxxxxxx"
export NEWS_GIST_ID="abc123def456"  # 선택

# 뉴스 브리핑 실행
PYTHONPATH=. python src/main.py news
```

로그에서 Gist 생성/사용 메시지 확인

---

## ⚠️ 주의사항

### GIST_TOKEN 보안

- **절대 공개하지 마세요!**
- GitHub Secrets에만 저장
- `.env` 파일에 저장 시 `.gitignore`에 포함 확인
- 토큰이 유출되면 즉시 GitHub에서 삭제하고 새로 생성

### Gist ID 관리

- Gist ID는 공개해도 되지만, Gist 자체는 비공개로 설정
- Gist를 삭제하면 저장된 상태가 사라집니다
- 여러 환경에서 같은 Gist를 사용하면 상태가 공유됩니다

---

## 📝 요약

### 필수 설정
- ✅ **GIST_TOKEN**: GitHub Personal Access Token (gist 권한)

### 선택 설정 (자동 생성 가능)
- 🔶 **NEWS_GIST_ID**: 뉴스 상태용 Gist ID
- 🔶 **SETTINGS_GIST_ID**: 설정용 Gist ID

### 설정 순서
1. GIST_TOKEN 생성 및 Secrets에 추가 (필수)
2. NEWS_GIST_ID, SETTINGS_GIST_ID는 자동 생성되므로 선택사항

---

## 🆘 문제 해결

### "GIST_TOKEN not set" 경고
- GitHub Secrets에 GIST_TOKEN이 설정되었는지 확인
- Secret 이름이 정확한지 확인 (대소문자 구분)

### "Failed to create Gist" 오류
- GIST_TOKEN의 `gist` 권한이 있는지 확인
- 토큰이 만료되지 않았는지 확인

### 중복 방지가 작동하지 않음
- GIST_TOKEN이 설정되었는지 확인
- GitHub Actions 로그에서 Gist 생성/사용 메시지 확인
- NEWS_GIST_ID가 올바르게 설정되었는지 확인

---

*Last Updated: 2025-12-04*

