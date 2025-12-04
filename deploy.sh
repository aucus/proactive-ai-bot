#!/bin/bash
# Proactive AI Bot 배포 스크립트

set -e

echo "🚀 Proactive AI Bot 배포 시작..."
echo ""

# 1. Git 초기화 확인
if [ ! -d .git ]; then
    echo "📦 Git 초기화..."
    git init
    git add .
    git commit -m "Initial commit: Proactive AI Telegram Bot"
    echo "✅ Git 초기화 완료"
else
    echo "ℹ️  Git repository 이미 존재"
fi

# 2. GitHub Repository 확인
if ! git remote | grep -q origin; then
    echo ""
    echo "⚠️  GitHub Repository가 연결되지 않았습니다."
    echo ""
    echo "다음 중 하나를 선택하세요:"
    echo ""
    echo "옵션 A: GitHub CLI 사용 (권장)"
    echo "  gh repo create proactive-ai-bot --public --source=. --remote=origin"
    echo "  git push -u origin main"
    echo ""
    echo "옵션 B: 수동으로 GitHub에서 생성 후"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/proactive-ai-bot.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    echo ""
    exit 1
fi

# 3. 변경사항 커밋
echo "📝 변경사항 확인..."
if [ -n "$(git status --porcelain)" ]; then
    git add .
    git commit -m "Update: $(date +%Y-%m-%d)" || true
fi

# 4. 푸시
echo "📤 GitHub에 푸시..."
git push -u origin main || git push

echo ""
echo "✅ 배포 완료!"
echo ""
echo "📋 다음 단계:"
echo "1. GitHub Repository → Settings → Secrets and variables → Actions"
echo "2. 다음 Secrets를 설정하세요:"
echo "   - TELEGRAM_TOKEN"
echo "   - TELEGRAM_CHAT_ID"
echo "   - GEMINI_API_KEY"
echo "3. Actions 탭에서 Workflow를 수동 실행하여 테스트하세요"
echo ""
