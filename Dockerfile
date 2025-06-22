# 自動生成されたDockerfile - 2025-06-22 03:33:35
FROM nvcr.io/nvidia/pytorch:25.05-py3

# ────────────── 基本 ENV ──────────────
ENV BNB_CUDA_VERSION=124
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# ────────────── uv設定 ──────────────
ENV UV_SYSTEM_PYTHON=1
ENV UV_CACHE_DIR=/opt/uv-cache
ENV UV_NO_PROGRESS=1

# ────────────── PEP 668制限の無効化 ──────────────
# Docker環境ではexternally managed制限を無効化
RUN rm -f /usr/lib/python*/EXTERNALLY-MANAGED
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# ────────────── OS パッケージ ──────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git build-essential cmake ninja-build wget \
    && rm -rf /var/lib/apt/lists/*

# ────────────── uv インストール ──────────────
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# uvのキャッシュディレクトリを作成
RUN mkdir -p ${UV_CACHE_DIR}

# uvインストール確認
RUN uv --version


# ────────────── Node.js ──────────────
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @anthropic-ai/claude-code


# ────────────── PyTorch ──────────────

# 既存のPyTorchを削除
RUN uv pip uninstall torch torchvision torchaudio || true

# PyTorchをuvでインストール（バージョン指定なし・CUDA自動選択）
RUN uv pip install \
    torch \
    torchvision \
    torchaudio \
    --index-url https://download.pytorch.org/whl/cu124


# ────────────── bitsandbytes（ソースからビルド） ──────────────
RUN git clone --depth 1 https://github.com/bitsandbytes-foundation/bitsandbytes.git && \
    cd bitsandbytes && \
    export BNB_CUDA_VERSION=124 && \
    cmake -DCOMPUTE_BACKEND=cuda -S . && \
    make -j$(nproc) && \
    pip install -e . && \
    cd .. && rm -rf bitsandbytes


# ────────────── xformers ──────────────
RUN uv pip install xformers



# ────────────── Flash-Attention ──────────────
# ビルド依存関係をuvでインストール
RUN uv pip install ninja packaging wheel setuptools

# Flash Attentionのビルドとインストール
RUN TORCH_CUDA_ARCH_LIST="9.0" \
    MAX_JOBS=$(nproc) \
    uv pip install flash-attn==2.8.0.post2 \
    --no-build-isolation




# ────────────── ライブラリの一括インストール ──────────────


RUN uv pip install "transformers>=4.51.3"

RUN uv pip install "accelerate>=1.7.0"

RUN uv pip install "peft>=0.15.2"

RUN uv pip install "datasets"

RUN uv pip install "sentencepiece"

RUN uv pip install "numpy"

RUN uv pip install "pandas"

RUN uv pip install "matplotlib"

RUN uv pip install "scipy"

RUN uv pip install "scikit-learn"

RUN uv pip install "jupyterlab"



# ────────────── uvキャッシュの最適化 ──────────────
RUN uv cache clean

# ────────────── 分散設定 ──────────────
ENV MASTER_ADDR=localhost
ENV MASTER_PORT=29500
ENV WORLD_SIZE=8

# ────────────── カスタム ENV ──────────────

ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

ENV NCCL_DEBUG=INFO

ENV NCCL_P2P_LEVEL=NVL


WORKDIR /mnt

# パッケージリストを記録
RUN uv pip list > /installed-packages.txt

# ヘルスチェック用スクリプト
RUN echo '#!/bin/bash\npython -c "import torch; assert torch.cuda.is_available()"' > /healthcheck.sh && \
    chmod +x /healthcheck.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD /healthcheck.sh || exit 1