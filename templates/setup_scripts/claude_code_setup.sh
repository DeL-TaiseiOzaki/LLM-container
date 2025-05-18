#!/bin/bash
# templates/setup_scripts/claude_code_setup.sh

# Claude Codeの初期設定を行うスクリプト

# 色の定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Claude Codeの初期設定を開始します...${NC}"

# Node.jsのバージョン確認
node_version=$(node --version)
echo -e "Node.jsバージョン: ${GREEN}${node_version}${NC}"

# npmのバージョン確認
npm_version=$(npm --version)
echo -e "npmバージョン: ${GREEN}${npm_version}${NC}"

# Claude Codeのインストール確認
if command -v claude &> /dev/null; then
    claude_version=$(claude --version)
    echo -e "Claude Codeバージョン: ${GREEN}${claude_version}${NC}"
else
    echo -e "${YELLOW}Claude Codeがインストールされていません。インストールします...${NC}"
    npm install -g @anthropic-ai/claude-code
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Claude Codeのインストールに失敗しました${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Claude Codeのインストールが完了しました${NC}"
fi

# 設定ディレクトリの作成
mkdir -p ~/.claude

# 初期設定の案内
echo -e "${BLUE}初期設定方法:${NC}"
echo -e "1. ${YELLOW}claude${NC} コマンドを実行してClaude Codeを起動します"
echo -e "2. Anthropicアカウントでの認証を完了します"
echo -e "3. コードベースに関する質問や操作が可能になります"
echo -e ""
echo -e "利用可能なスラッシュコマンド:"
echo -e "  /help       - ヘルプの表示"
echo -e "  /clear      - 会話履歴のクリア"
echo -e "  /config     - 設定パネルを開く"
echo -e "  /bug        - フィードバックの送信"
echo -e "  /logout     - ログアウト"
echo -e ""
echo -e "${GREEN}Claude Codeの初期設定が完了しました${NC}"