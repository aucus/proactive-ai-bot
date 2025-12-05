"""Google OAuth Refresh Token 발급 스크립트

사용법:
1. Google Cloud Console에서 Client ID와 Secret을 발급받으세요
2. 아래 YOUR_CLIENT_ID와 YOUR_CLIENT_SECRET을 실제 값으로 변경하세요
3. 이 스크립트를 실행하세요: python get_refresh_token.py
4. 브라우저에서 Google 계정으로 로그인하고 권한을 승인하세요
5. 콘솔에 출력된 Refresh Token을 .env 파일에 추가하세요
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# OAuth 2.0 스코프 (Calendar 읽기 전용)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_refresh_token():
    """Refresh Token 발급"""
    
    print("="*60)
    print("Google OAuth Refresh Token 발급 도구")
    print("="*60)
    print("\n⚠️  먼저 Google Cloud Console에서 다음을 완료하세요:")
    print("   1. 프로젝트 생성")
    print("   2. Google Calendar API 활성화")
    print("   3. OAuth 동의 화면 설정")
    print("   4. OAuth 클라이언트 ID 생성 (데스크톱 앱)")
    print("\n" + "="*60)
    
    # 사용자로부터 Client ID와 Secret 입력받기
    client_id = input("\nClient ID를 입력하세요: ").strip()
    if not client_id:
        print("❌ Client ID가 필요합니다.")
        return None
    
    client_secret = input("Client Secret을 입력하세요: ").strip()
    if not client_secret:
        print("❌ Client Secret이 필요합니다.")
        return None
    
    # credentials.json 파일 생성
    credentials_data = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    credentials_file = 'credentials.json'
    with open(credentials_file, 'w', encoding='utf-8') as f:
        json.dump(credentials_data, f, indent=2)
    
    print(f"\n✅ {credentials_file} 파일이 생성되었습니다.")
    print("\n브라우저가 열리면:")
    print("  1. Google 계정으로 로그인하세요")
    print("  2. '앱이 확인되지 않았습니다' 경고가 나오면 '고급' → 'Proactive AI Bot(으)로 이동' 클릭")
    print("  3. 권한을 승인하세요")
    print("\n잠시만 기다려주세요...\n")
    
    try:
        # OAuth 플로우 시작
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
        
        # Refresh Token 추출
        refresh_token = creds.refresh_token
        
        if not refresh_token:
            print("\n❌ Refresh Token을 가져올 수 없습니다.")
            print("   Access Token만 발급되었을 수 있습니다.")
            print("   OAuth 동의 화면 설정을 확인하세요.")
            return None
        
        print("\n" + "="*60)
        print("✅ Refresh Token 발급 완료!")
        print("="*60)
        print(f"\n다음 값을 .env 파일에 추가하세요:\n")
        print(f"GOOGLE_CLIENT_ID={client_id}")
        print(f"GOOGLE_CLIENT_SECRET={client_secret}")
        print(f"GOOGLE_REFRESH_TOKEN={refresh_token}")
        print("\n" + "="*60)
        
        # credentials.json 삭제 (보안)
        if os.path.exists(credentials_file):
            os.remove(credentials_file)
            print(f"\n✅ {credentials_file} 파일이 삭제되었습니다. (보안)")
        
        return refresh_token
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n문제 해결:")
        print("  1. Client ID와 Secret이 올바른지 확인하세요")
        print("  2. Google Calendar API가 활성화되었는지 확인하세요")
        print("  3. OAuth 동의 화면이 올바르게 설정되었는지 확인하세요")
        return None
    
    finally:
        # 정리
        if os.path.exists(credentials_file):
            try:
                os.remove(credentials_file)
            except:
                pass


if __name__ == "__main__":
    get_refresh_token()

