# Google Calendar API OAuth 인증 설정 가이드

## 📋 개요

Google Calendar API를 사용하여 일정 정보를 가져오기 위해서는 OAuth 2.0 인증이 필요합니다.
이 가이드는 다음 3가지 값을 얻는 방법을 설명합니다:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`

---

## 🔧 단계별 설정

### 1단계: Google Cloud Console 프로젝트 생성

1. **Google Cloud Console 접속**
   - https://console.cloud.google.com/ 접속
   - Google 계정으로 로그인

2. **새 프로젝트 생성**
   - 상단 프로젝트 선택 드롭다운 클릭
   - **"새 프로젝트"** 클릭
   - 프로젝트 이름 입력 (예: `proactive-ai-bot`)
   - **"만들기"** 클릭
   - 프로젝트 생성 완료까지 대기 (1-2분)

---

### 2단계: Google Calendar API 활성화

1. **API 및 서비스 → 라이브러리**
   - 왼쪽 메뉴에서 **"API 및 서비스"** → **"라이브러리"** 클릭

2. **Google Calendar API 검색 및 활성화**
   - 검색창에 "Google Calendar API" 입력
   - **"Google Calendar API"** 선택
   - **"사용 설정"** 버튼 클릭
   - 활성화 완료까지 대기

---

### 3단계: OAuth 2.0 클라이언트 ID 생성

1. **OAuth 동의 화면 설정**
   - 왼쪽 메뉴에서 **"API 및 서비스"** → **"OAuth 동의 화면"** 클릭
   - 사용자 유형 선택: **"외부"** (개인용이면 외부로도 가능)
   - **"만들기"** 클릭

2. **앱 정보 입력**
   ```
   앱 이름: Proactive AI Bot (또는 원하는 이름)
   사용자 지원 이메일: 본인 이메일
   앱 로고: (선택사항)
   ```
   - **"저장 후 다음"** 클릭

3. **범위(Scopes) 설정**
   - **"범위 추가 또는 삭제"** 클릭
   - 다음 범위 추가:
     ```
     https://www.googleapis.com/auth/calendar.readonly
     ```
   - **"업데이트"** → **"저장 후 다음"** 클릭

4. **테스트 사용자 추가** (외부 앱인 경우)
   - 본인 Google 계정 이메일 추가
   - **"저장 후 다음"** 클릭

5. **요약 확인**
   - 정보 확인 후 **"대시보드로 돌아가기"** 클릭

📌 **중요: Testing 상태의 Refresh Token 만료**
- OAuth 동의 화면 **게시 상태(Publishing status)가 "Testing"** 인 경우, (테스트 사용자로 발급된) **Refresh Token이 7일 후 만료**될 수 있습니다.
- **주기적 재발급이 싫다면** 게시 상태를 **"In production"** 으로 전환하는 것이 가장 확실한 방법입니다.
  - 개인 사용(본인만 사용)이라면 **검증(verification) 없이도** 전환은 가능하지만, 브라우저에서 **"앱이 확인되지 않았습니다"** 경고가 계속 나올 수 있습니다.

---

### 4단계: OAuth 2.0 클라이언트 ID 및 Secret 발급

1. **사용자 인증 정보 생성**
   - 왼쪽 메뉴에서 **"API 및 서비스"** → **"사용자 인증 정보"** 클릭
   - 상단 **"+ 사용자 인증 정보 만들기"** 클릭
   - **"OAuth 클라이언트 ID"** 선택

2. **애플리케이션 유형 선택**
   - 애플리케이션 유형: **"데스크톱 앱"** 선택
   - 이름: `Proactive AI Bot` (또는 원하는 이름)

3. **클라이언트 ID 및 Secret 확인**
   - **"만들기"** 클릭
   - 팝업에서 다음 정보 확인:
     ```
     클라이언트 ID: xxxxxx.apps.googleusercontent.com
     클라이언트 보안 비밀번호: xxxxxx
     ```
   - **⚠️ 중요: 이 정보를 복사해두세요! (나중에 다시 볼 수 없습니다)**

---

### 5단계: Refresh Token 발급

Refresh Token은 보통 “장기 사용”이 가능하지만, **OAuth 동의 화면 상태/정책에 따라 만료(무효화)**될 수 있습니다.

- **OAuth 동의 화면이 "Testing"**: Refresh Token이 **7일 후 만료**될 수 있어 **주기적 재발급**이 필요합니다.
- **OAuth 동의 화면이 "In production"**: 보통 **1회 발급 후 장기 사용**이 가능합니다. (단, 권한 철회/장기간 미사용 등으로 무효화 가능)

#### 방법 A: Python 스크립트 사용 (권장)

1. **임시 스크립트 생성**
   ```bash
   # 프로젝트 루트에 get_refresh_token.py 생성
   ```

2. **스크립트 내용** (`get_refresh_token.py`):
   ```python
   """Google OAuth Refresh Token 발급 스크립트"""
   
   import os
   from google_auth_oauthlib.flow import InstalledAppFlow
   from google.auth.transport.requests import Request
   import json
   
   # OAuth 2.0 스코프
   SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
   
   def get_refresh_token():
       """Refresh Token 발급"""
       
       # 클라이언트 ID와 Secret을 credentials.json으로 저장
       credentials_data = {
           "installed": {
               "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
               "client_secret": "YOUR_CLIENT_SECRET",
               "auth_uri": "https://accounts.google.com/o/oauth2/auth",
               "token_uri": "https://oauth2.googleapis.com/token",
               "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
               "redirect_uris": ["http://localhost"]
           }
       }
       
       # credentials.json 파일 생성
       with open('credentials.json', 'w') as f:
           json.dump(credentials_data, f, indent=2)
       
       print("credentials.json 파일이 생성되었습니다.")
       print("브라우저가 열리면 Google 계정으로 로그인하고 권한을 승인하세요.\n")
       
       # OAuth 플로우 시작
       flow = InstalledAppFlow.from_client_secrets_file(
           'credentials.json', SCOPES)
       creds = flow.run_local_server(port=0)
       
       # Refresh Token 추출
       refresh_token = creds.refresh_token
       
       print("\n" + "="*50)
       print("✅ Refresh Token 발급 완료!")
       print("="*50)
       print(f"\nGOOGLE_REFRESH_TOKEN={refresh_token}\n")
       print("이 값을 .env 파일에 추가하세요.")
       print("="*50)
       
       # credentials.json 삭제 (보안)
       os.remove('credentials.json')
       print("\ncredentials.json 파일이 삭제되었습니다.")
       
       return refresh_token
   
   if __name__ == "__main__":
       get_refresh_token()
   ```

3. **스크립트 실행**
   ```bash
   # (macOS/Homebrew Python) PEP 668 이슈로 시스템 파이썬에 pip install이 막힐 수 있어요.
   # 프로젝트 로컬 가상환경(.venv)을 만들어 설치하는 방식을 권장합니다.
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   
   # 스크립트 실행
   .venv/bin/python get_refresh_token.py
   ```

4. **인증 과정**
   - 브라우저가 자동으로 열림
   - Google 계정 선택 및 로그인
   - **"앱이 확인되지 않았습니다"** 경고가 나오면 **"고급"** → **"Proactive AI Bot(으)로 이동"** 클릭
   - 권한 승인
   - 콘솔에 Refresh Token 출력

#### 방법 B: Google OAuth Playground 사용 (간단)

1. **Google OAuth Playground 접속**
   - https://developers.google.com/oauthplayground/ 접속

2. **설정 변경**
   - 오른쪽 상단 **⚙️ 설정** 클릭
   - **"Use your own OAuth credentials"** 체크
   - Client ID와 Client Secret 입력
   - **"Close"** 클릭

3. **스코프 선택**
   - 왼쪽에서 다음 스코프 찾기:
     ```
     https://www.googleapis.com/auth/calendar.readonly
     ```
   - 체크박스 선택
   - **"Authorize APIs"** 클릭

4. **인증 및 토큰 발급**
   - Google 계정 로그인 및 권한 승인
   - **"Exchange authorization code for tokens"** 클릭
   - 오른쪽 패널에서 **"Refresh token"** 값 복사

---

### 6단계: 환경변수 설정

#### 로컬 개발 (.env 파일)

`.env` 파일에 다음 값 추가:

```bash
# Google Calendar API
GOOGLE_CLIENT_ID=xxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxxx
GOOGLE_REFRESH_TOKEN=xxxxxx
```

#### GitHub Actions (Secrets)

1. **Repository → Settings → Secrets and variables → Actions**
2. **New repository secret** 클릭
3. 다음 3개 Secret 추가:
   - `GOOGLE_CLIENT_ID`: 클라이언트 ID 값
   - `GOOGLE_CLIENT_SECRET`: 클라이언트 Secret 값
   - `GOOGLE_REFRESH_TOKEN`: Refresh Token 값

---

## ✅ 테스트

설정이 완료되었는지 확인:

```bash
# 로컬에서 테스트
python src/main.py schedule
```

성공하면 오늘 일정이 Telegram으로 전송됩니다!

---

## 🔒 보안 주의사항

1. **절대 공개하지 마세요**
   - Client ID, Client Secret, Refresh Token은 모두 비밀 정보입니다
   - GitHub에 커밋하지 마세요 (`.env`는 `.gitignore`에 포함되어 있음)
   - GitHub Secrets에만 저장하세요

2. **Refresh Token 만료 시**
   - **Testing 상태면 7일 만료**가 발생할 수 있어, 만료 시 5단계를 다시 진행해야 합니다
   - Production 상태에서도 다음 경우 Refresh Token이 무효화될 수 있습니다:
     - 사용자가 앱 접근 권한을 철회(revoke)
     - 장기간 미사용(예: 6개월 이상)로 인한 만료
     - 동일 사용자/클라이언트에서 Refresh Token을 너무 많이 발급받아 오래된 토큰이 무효화(토큰 개수 제한)

3. **프로덕션 환경**
   - 프로덕션에서는 OAuth 동의 화면을 "프로덕션"으로 승인받는 것을 권장합니다
   - 테스트 사용자 제한이 없어집니다

---

## 🐛 문제 해결

### "invalid_grant" 오류
- Refresh Token이 만료되었거나 잘못되었습니다
- 5단계를 다시 진행하여 새 Refresh Token 발급

### "access_denied" 오류
- OAuth 동의 화면에서 권한을 거부했습니다
- 5단계를 다시 진행하여 권한 승인

### "redirect_uri_mismatch" 오류
- OAuth 클라이언트 ID 설정에서 리다이렉트 URI가 맞지 않습니다
- "데스크톱 앱" 유형을 사용하면 자동으로 처리됩니다

### 일정이 안 나올 때
- Google Calendar에 실제 일정이 있는지 확인
- `calendar_id`가 "primary"인지 확인 (기본 캘린더)
- 로그 확인: `logger.info`로 API 응답 확인

---

## 📚 참고 자료

- [Google Calendar API 문서](https://developers.google.com/calendar/api)
- [OAuth 2.0 가이드](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)

---

*Last Updated: 2025-12-04*

