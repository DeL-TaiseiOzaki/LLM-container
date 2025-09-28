#!/bin/bash

# Simple Multi-User LLM Container Launcher
# 使い方: ./run.sh ユーザー名 [GPUオプション] [ポートオフセット]

set -e

# パラメータ
USER=${1:-$(whoami)}
GPU=${2:-all}
PORT_OFFSET=${3:-0}

# 基本設定
CONTAINER="llm-${USER}"
IMAGE="llm-env:latest"
JUPYTER_PORT=$((8888 + PORT_OFFSET))
TENSORBOARD_PORT=$((6006 + PORT_OFFSET))

echo "🚀 LLM Container for ${USER}"
echo "  Container: ${CONTAINER}"
echo "  GPU: ${GPU}"
echo "  Jupyter: http://localhost:${JUPYTER_PORT}"
echo "  TensorBoard: http://localhost:${TENSORBOARD_PORT}"
echo ""

# 既存コンテナチェック
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        echo "⚠️  既に実行中です"
        echo "接続: docker exec -it ${CONTAINER} bash"
        exit 0
    fi
    echo "再起動中..."
    docker start ${CONTAINER}
    exit 0
fi

# ワークスペース作成
mkdir -p workspace/${USER}
mkdir -p cache/${USER}

# GPU設定
if [ "${GPU}" = "all" ]; then
    GPU_FLAG="--gpus all"
else
    GPU_FLAG="--gpus device=${GPU}"
fi

# コンテナ起動
docker run ${GPU_FLAG} \
  --name ${CONTAINER} \
  -v $(pwd)/workspace/${USER}:/workspace \
  -v $(pwd)/cache/${USER}:/root/.cache \
  -p ${JUPYTER_PORT}:8888 \
  -p ${TENSORBOARD_PORT}:6006 \
  --shm-size 16g \
  -e USER=${USER} \
  --hostname ${CONTAINER} \
  -it -d \
  ${IMAGE}

echo "✅ 起動完了"
echo "接続: docker exec -it ${CONTAINER} bash"