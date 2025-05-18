# 自動生成されたDockerfile - 2025-05-18 17:26:36
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

# ────────────── PyTorch ──────────────
RUN pip uninstall -y torch torchvision torchaudio || true
RUN pip install torch==2.7.0 torchvision==2.7.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu128

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
    pip install "flash-attn==2.7.4.post1" --no-build-isolation

# ────────────── Triton ──────────────
RUN pip install -U --index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/Triton-Nightly/pypi/simple/ triton-nightly

# ────────────── 追加 Python ライブラリ ──────────────
RUN pip install --no-cache-dir \
    transformers>=4.41.0 \
    peft>=0.10.0 \
    accelerate>=0.29.3 \
    deepspeed \
    trl>=0.8.6 \
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
    einops \
    && echo "Python libraries installed successfully"


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

