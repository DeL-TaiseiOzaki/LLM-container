#!/bin/bash
# templates/setup_scripts/jupyter_setup.sh

# Jupyter Lab設定スクリプト

# 色の定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Jupyter Lab設定を開始します...${NC}"

# 設定ディレクトリの確認と作成
JUPYTER_CONFIG_DIR=~/.jupyter
if [ ! -d "$JUPYTER_CONFIG_DIR" ]; then
    mkdir -p $JUPYTER_CONFIG_DIR
    echo -e "Jupyter設定ディレクトリを作成しました: ${GREEN}$JUPYTER_CONFIG_DIR${NC}"
fi

# Jupyter設定ファイルの生成
jupyter lab --generate-config
if [ $? -ne 0 ]; then
    echo -e "${RED}Jupyter Lab設定ファイルの生成に失敗しました${NC}"
    exit 1
fi

# パスワード設定のガイダンス
echo -e "${YELLOW}Jupyter Labのパスワード設定を行います${NC}"
echo -e "以下のコマンドを実行してパスワードを設定します:"
echo -e "  ${GREEN}jupyter lab password${NC}"
echo -e "または、トークン認証を使用することも可能です"

# Jupyter Lab拡張機能のインストール
echo -e "${BLUE}有用なJupyter Lab拡張機能をインストールしています...${NC}"

# JupyterLabのバージョン確認
jupyter_version=$(jupyter --version | grep "jupyter_core" | awk '{print $4}')
echo -e "Jupyter Core バージョン: ${GREEN}${jupyter_version}${NC}"

# 拡張機能のインストール
pip install -q jupyterlab-git jupyterlab-lsp jupyterlab-code-formatter jupyterlab-widgets ipywidgets
jupyter lab build

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}一部の拡張機能のインストールに問題がありましたが、基本機能は動作します${NC}"
else
    echo -e "${GREEN}Jupyter Lab拡張機能のインストールが完了しました${NC}"
fi

# Jupyter Lab起動方法の案内
echo -e "${BLUE}Jupyter Labの起動方法:${NC}"
echo -e "以下のコマンドでJupyter Labを起動できます:"
echo -e "  ${GREEN}jupyter lab --ip 0.0.0.0 --allow-root --no-browser${NC}"
echo -e "ブラウザで以下のURLにアクセスします:"
echo -e "  ${GREEN}http://localhost:8888/${NC}"
echo -e "または、コンテナのIPアドレスと表示されるトークンを使用してアクセスします"
echo -e ""
echo -e "${GREEN}Jupyter Lab設定が完了しました${NC}"