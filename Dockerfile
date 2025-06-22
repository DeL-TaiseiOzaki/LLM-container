# 自動生成されたDockerfile - 2025-06-22 01:40:56
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

# ────────────── OS パッケージ ──────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git build-essential cmake ninja-build wget \
    && rm -rf /var/lib/apt/lists/*

# ────────────── uv インストール ──────────────
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.cargo/bin/uv /usr/local/bin/

# uvのキャッシュディレクトリを作成
RUN mkdir -p ${UV_CACHE_DIR}


# ────────────── Node.js (uv経由でnodeenvを使用) ──────────────
RUN uv pip install nodeenv && \
    nodeenv -p --node=lts && \
    npm install -g @anthropic-ai/claude-code


# ────────────── PyTorch ──────────────

# 既存のPyTorchを削除
RUN uv pip uninstall torch torchvision torchaudio || true

# PyTorchをuvでインストール

RUN uv pip install \
    torch==2.7.0 \
    torchvision \
    torchaudio \
    --index-url https://download.pytorch.org/whl/cu124


# ────────────── bitsandbytes（ソースからビルド） ──────────────
# bitsandbytesは特殊なビルドが必要なので従来通り
RUN git clone --depth 1 https://github.com/bitsandbytes-foundation/bitsandbytes.git && \
    cd bitsandbytes && \
    export BNB_CUDA_VERSION=124 && \
    cmake -DCOMPUTE_BACKEND=cuda -S . && \
    make -j$(nproc) && \
    pip install -e . && \
    cd .. && rm -rf bitsandbytes


# ────────────── xformers ──────────────
RUN uv pip install \
    xformers==0.0.30 \
    --index-url https://download.pytorch.org/whl/124



# ────────────── Flash-Attention ──────────────
# ビルド依存関係をuvでインストール
RUN uv pip install ninja packaging wheel setuptools

# Flash Attentionのビルドとインストール
RUN TORCH_CUDA_ARCH_LIST="9.0" \
    MAX_JOBS=$(nproc) \
    uv pip install flash-attn==2.8.0.post2 \
    --no-build-isolation




# ────────────── ライブラリの一括インストール ──────────────

# requirements.txtを直接作成（heredoc を使わずに）


RUN echo "transformers>=4.51.3" >> /tmp/requirements.txt



RUN echo "accelerate>=1.7.0" >> /tmp/requirements.txt



RUN echo "peft>=0.15.2" >> /tmp/requirements.txt



RUN echo "datasets" >> /tmp/requirements.txt



RUN echo "sentencepiece" >> /tmp/requirements.txt



RUN echo "numpy" >> /tmp/requirements.txt



RUN echo "pandas" >> /tmp/requirements.txt



RUN echo "matplotlib" >> /tmp/requirements.txt



RUN echo "scipy" >> /tmp/requirements.txt



RUN echo "scikit-learn" >> /tmp/requirements.txt



RUN echo "jupyterlab" >> /tmp/requirements.txt



# uvで一括インストール（並列処理で高速化）
RUN uv pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt


# ────────────── uvキャッシュの最適化 ──────────────
# 不要なキャッシュを削除してイメージサイズを削減
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