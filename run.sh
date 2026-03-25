#!/bin/bash
set -e

# パラメータ
export USER=${1:-$(whoami)}
export BASE_DIR=${2:-$(pwd)/users/${USER}}
CONTAINER="llm-${USER}"
IMAGE="llm-env:latest"

# Docker コマンド（sudo が必要な場合は自動判定）
DOCKER_CMD="docker"
if ! docker ps >/dev/null 2>&1; then
    echo "⚠️  Dockerにsudoが必要です"
    DOCKER_CMD="sudo docker"
fi

echo "🚀 LLM Container for ${USER}"
echo "📁 Base Directory: ${BASE_DIR}"
echo ""

# 必要なディレクトリを作成
echo "📂 Creating directories..."
mkdir -p ${BASE_DIR}/workspace
mkdir -p ${BASE_DIR}/models
mkdir -p ${BASE_DIR}/datasets
mkdir -p ${BASE_DIR}/logs
sudo mkdir -p /data/cache/huggingface
sudo mkdir -p /data/cache/uv
sudo mkdir -p /data/cache/torch
sudo mkdir -p /data/cache/matplotlib
sudo mkdir -p /data/cache/ts-queue/logs
sudo chmod 1777 /data/cache/ts-queue/logs

# 既存コンテナの確認
if $DOCKER_CMD ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "📦 Container ${CONTAINER} already exists"
    if $DOCKER_CMD ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        echo "✅ Container is already running"
    else
        echo "🔄 Starting existing container..."
        $DOCKER_CMD start ${CONTAINER}
    fi
else
    # 新規コンテナ作成
    echo "🐳 Creating and starting new container..."
    $DOCKER_CMD run -d \
        --name ${CONTAINER} \
        --gpus all \
        --network host \
        --restart unless-stopped \
        -v ${BASE_DIR}/workspace:/workspace \
        -v ${BASE_DIR}/models:/models \
        -v ${BASE_DIR}/datasets:/datasets \
        -v ${BASE_DIR}/logs:/logs \
        -v /data/cache/huggingface:/cache/huggingface \
        -v /data/cache/uv:/cache/uv \
        -v /data/cache/torch:/cache/torch \
        -v /data/cache/matplotlib:/cache/matplotlib \
        -v /data/cache/ts-queue:/cache/ts-queue \
        -v /usr/local/bin/ts:/usr/local/bin/ts:ro \
        -v /usr/local/bin/q:/usr/local/bin/q:ro \
        --hostname ${CONTAINER} \
        -e XDG_CACHE_HOME=/cache \
        -e HF_HOME=/cache/huggingface \
        -e HF_HUB_CACHE=/cache/huggingface/hub \
        -e UV_CACHE_DIR=/cache/uv \
        -e TORCH_HOME=/cache/torch \
        -e MPLCONFIGDIR=/cache/matplotlib \
        -e TS_SOCKET=/cache/ts-queue/.socket \
        -e ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-} \
        -e OPENAI_API_KEY=${OPENAI_API_KEY:-} \
        -e HF_TOKEN=${HF_TOKEN:-} \
        -it \
        ${IMAGE}
fi

echo ""
echo "✅ 起動完了"
echo ""
echo "📁 ストレージ:"
echo "  作業: ${BASE_DIR}/workspace → /workspace"
echo "  モデル: ${BASE_DIR}/models → /models"
echo "  データ: ${BASE_DIR}/datasets → /datasets"
echo "  ログ: ${BASE_DIR}/logs → /logs"
echo "  キャッシュ: /data/cache → /cache"
echo ""
echo "📝 接続: docker exec -it ${CONTAINER} bash"
echo ""