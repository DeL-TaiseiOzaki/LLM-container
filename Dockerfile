# 自動生成されたDockerfile - 2025-06-12 05:43:36
FROM nvcr.io/nvidia/pytorch:24.05-py3

# ────────────── 基本 ENV ──────────────
ENV BNB_CUDA_VERSION=128
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# ────────────── OS パッケージ ──────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git build-essential cmake ninja-build wget \
    && rm -rf /var/lib/apt/lists/*

# ────────────── Node.js（nvm使用）──────────────
ENV NVM_DIR="/root/.nvm"
ENV NODE_VERSION="lts"

# 既存のNode.jsを完全に削除
RUN apt-get update && \
    apt-get purge -y nodejs npm && \
    apt-get autoremove -y && \
    rm -rf /usr/local/lib/node_modules /usr/local/bin/node /usr/local/bin/npm /usr/bin/node /usr/bin/npm && \
    rm -rf /var/lib/apt/lists/*

# nvmをインストールし、指定されたNode.jsバージョンをインストール
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && \
    export NVM_DIR="/root/.nvm" && \
    . "$NVM_DIR/nvm.sh" && \
    if [ "$NODE_VERSION" = "lts" ]; then \
         nvm install --lts && nvm use --lts && nvm alias default lts/*; \
    elif [ "$NODE_VERSION" = "latest" ] || [ "$NODE_VERSION" = "current" ]; then \
         nvm install node && nvm use node && nvm alias default node; \
    else \
         nvm install "$NODE_VERSION" && nvm use "$NODE_VERSION" && nvm alias default "$NODE_VERSION"; \
    fi && \
    # 動的にPATHを設定
    NODE_PATH=$(find $NVM_DIR/versions/node -maxdepth 1 -type d | tail -1) && \
    echo "export PATH=$NODE_PATH/bin:\
$PATH" >> ~/.bashrc

# シェル起動時にnvmが自動読み込みされるよう設定
RUN echo 'export NVM_DIR="/root/.nvm"' >> ~/.bashrc && \
    echo '[ -s "$NVM_DIR/nvm.sh" ] && \
. "$NVM_DIR/nvm.sh"' >> ~/.bashrc && \
    echo '[ -s "$NVM_DIR/bash_completion" ] && \
. "$NVM_DIR/bash_completion"' >> ~/.bashrc

# Claude Codeのインストール（nvmを明示的に読み込んでから）
RUN bash -c "source /root/.nvm/nvm.sh && npm install -g @anthropic-ai/claude-code"

# ────────────── PyTorch ──────────────
RUN pip uninstall -y torch torchvision torchaudio || true
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# ────────────── bitsandbytes（手動ビルド） ──────────────
RUN git clone --depth 1 https://github.com/bitsandbytes-foundation/bitsandbytes.git && \
    cd bitsandbytes && \
    export BNB_CUDA_VERSION=128 && \
    cmake -DCOMPUTE_BACKEND=cuda -S . && \
    make -j$(nproc) && \
    pip install -e . && \
    cd .. && rm -rf bitsandbytes

# ────────────── xformers ──────────────
RUN pip install -U "xformers==0.0.30" \
    --index-url https://download.pytorch.org/whl/cu128 --no-deps

# ────────────── Flash-Attention ──────────────
RUN pip install ninja && \
    pip install flash-attn --no-build-isolation

# ────────────── Triton ──────────────
RUN pip install -U --index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/Triton-Nightly/pypi/simple/ triton-nightly

# ────────────── 追加 Python ライブラリ ──────────────
RUN pip install --no-cache-dir \
    transformers>=4.41.0 \
    peft>=0.10.0 \
    accelerate>=0.29.3 \
    deepspeed \
    trl>=0.10.0 \
    packaging \
    ninja \
    datasets \
    huggingface_hub \
    sentencepiece \
    tokenizers \
    safetensors \
    evaluate \
    numpy \
    pandas \
    wandb \
    jupyterlab \
    ipywidgets \
    tqdm \
    einops    && echo "Python libraries installed successfully"

# ────────────── 分散設定（必要に応じて） ──────────────
ENV MASTER_ADDR=localhost
ENV MASTER_PORT=29500
ENV WORLD_SIZE=4

# ────────────── カスタム ENV ──────────────
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
ENV NCCL_DEBUG=INFO
ENV NCCL_P2P_LEVEL=NVL
ENV NCCL_IB_DISABLE=0
ENV NCCL_SOCKET_IFNAME=^lo,docker
ENV OMP_NUM_THREADS=8
ENV CUDA_DEVICE_MAX_CONNECTIONS=1

WORKDIR /mnt

# ────────────── 動作チェック ──────────────
# Node.js & npm バージョン確認（nvmを明示的に読み込んでから）
RUN bash -c "source /root/.nvm/nvm.sh && echo 'Node.js version: $(node --version)' && echo 'npm version: $(npm --version)'"

RUN python - <<'PY'
import torch, importlib
print("CUDA available:", torch.cuda.is_available())
print("GPU count:", torch.cuda.device_count())
for mod in ("flash_attn","transformers","vllm","lightllm","torchtune","unsloth"):
    try:
        m=importlib.import_module(mod)
        print(mod, getattr(m,"__version__", "imported"))
    except ImportError:
        pass
PY

RUN python - <<'PY'
import torch
[print(f"GPU {i}: {torch.cuda.get_device_name(i)}") for i in range(torch.cuda.device_count())]
PY