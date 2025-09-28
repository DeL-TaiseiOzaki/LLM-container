#!/bin/bash
set -e

# パラメータ
USER=${1:-$(whoami)}
BASE_DIR=${2:-$(pwd)}  # デフォルトは現在のディレクトリ
CONTAINER="llm-${USER}"
IMAGE="llm-env:12.8"

# Docker実行コマンド（sudo が必要な場合は自動判定）
DOCKER_CMD="docker"
if ! docker ps >/dev/null 2>&1; then
    echo "⚠️  Dockerにsudoが必要です"
    DOCKER_CMD="sudo docker"
fi

echo "🚀 LLM Container for ${USER}"
echo "📁 Base Directory: ${BASE_DIR}"
echo ""

# 既存コンテナチェック
if $DOCKER_CMD ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    if $DOCKER_CMD ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        echo "⚠️  既に実行中です"
        echo "接続: $DOCKER_CMD exec -it ${CONTAINER} bash"
        exit 0
    fi
    echo "再起動中..."
    $DOCKER_CMD start ${CONTAINER}
    $DOCKER_CMD logs ${CONTAINER} --tail 20
    exit 0
fi

# ディレクトリ作成
echo "📂 Creating directories under ${BASE_DIR}..."
mkdir -p ${BASE_DIR}/workspace
mkdir -p ${BASE_DIR}/models
mkdir -p ${BASE_DIR}/datasets
mkdir -p ${BASE_DIR}/logs
mkdir -p ${BASE_DIR}/.cache/huggingface

# コンテナ起動（ホストネットワークモード = 全ポート利用可能）
$DOCKER_CMD run \
  --gpus all \
  --name ${CONTAINER} \
  -v ${BASE_DIR}/workspace:/workspace \
  -v ${BASE_DIR}/models:/models \
  -v ${BASE_DIR}/datasets:/datasets \
  -v ${BASE_DIR}/logs:/logs \
  -v ${BASE_DIR}/.cache/huggingface:/root/.cache/huggingface \
  -e USER=${USER} \
  -e HF_HOME=/root/.cache/huggingface \
  -it -d \
  ${IMAGE}

echo "✅ 起動完了"
echo ""
echo "📁 ストレージ:"
echo "  作業: ${BASE_DIR}/workspace → /workspace"
echo "  モデル: ${BASE_DIR}/models → /models"
echo "  データ: ${BASE_DIR}/datasets → /datasets"
echo "  ログ: ${BASE_DIR}/logs → /logs"
echo ""
echo "📝 接続: $DOCKER_CMD exec -it ${CONTAINER} bash"
echo ""