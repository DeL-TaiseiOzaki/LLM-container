# ベースイメージを変更 - CUDA 12.8対応の最新NVIDIA公式コンテナを使用
FROM nvcr.io/nvidia/pytorch:24.05-py3

# 環境変数設定
ENV BNB_CUDA_VERSION=128
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# OS パッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    build-essential \
    cmake \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------------------
# 1. 既存のPyTorchのバージョンを確認
# --------------------------------------------------------------------------------
RUN python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.version.cuda}')"

# --------------------------------------------------------------------------------
# 2. bitsandbytesをソースからビルド（CUDA 12.8対応）
# --------------------------------------------------------------------------------
RUN git clone https://github.com/bitsandbytes-foundation/bitsandbytes.git && \
    cd bitsandbytes && \
    export BNB_CUDA_VERSION=128 && \
    cmake -DCOMPUTE_BACKEND=cuda -S . && \
    make && \
    pip install -e . && \
    cd .. && \
    echo "Attempting to verify bitsandbytes installation..." && \
    python -c "import bitsandbytes; print(f'bitsandbytes installed successfully: {bitsandbytes.__version__}')" || echo "Warning: bitsandbytes import test failed but continuing build"

# --------------------------------------------------------------------------------
# 3. xformersをCUDA 12.8対応版でインストール
# --------------------------------------------------------------------------------
RUN pip install -U "xformers<0.0.26" --no-deps && \
    echo "Attempting to verify xformers installation..." && \
    python -c "import xformers; print(f'xformers installed successfully')" || echo "Warning: xformers import test failed but continuing build"

# --------------------------------------------------------------------------------
# 4. 必要な依存関係をインストール
# --------------------------------------------------------------------------------
RUN pip install --no-cache-dir \
    transformers>=4.40.0 \
    sentencepiece \
    accelerate>=0.29.3 \
    trl>=0.8.6 \
    peft>=0.10.0 \
    datasets \
    safetensors \
    einops

# --------------------------------------------------------------------------------
# 5. UnslothをGitHubから直接インストール（最新版）
# --------------------------------------------------------------------------------
RUN pip install --no-cache-dir "unsloth @ git+https://github.com/unslothai/unsloth.git" && \
    echo "Attempting to verify unsloth installation..." && \
    python -c "import unsloth; print('Unsloth installed successfully')" || echo "Warning: unsloth import test failed but continuing build"

# --------------------------------------------------------------------------------
# 6. その他必要なライブラリ
# --------------------------------------------------------------------------------
RUN pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib \
    scipy \
    scikit-learn \
    scikit-image \
    wandb \
    jupyterlab \
    ipywidgets \
    pyarrow \
    polars \
    faiss-gpu \
    tqdm \
    openai \
    anthropic \
    evaluate \
    huggingface_hub \
    "optimum[onnxruntime-gpu]" \
    langchain \
    "llama-index>=0.10.0" \
    "ray[default]" \
    black \
    flake8 \
    isort \
    mypy \
    pre-commit \
    vllm \
    deepspeed \
    ninja \
    packaging \
    wheel \
    setuptools

# H100（Hopper）アーキテクチャ向け最適化設定
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
ENV NCCL_DEBUG=INFO
ENV NCCL_P2P_LEVEL=NVL

# Unslothトレーニング用の環境変数
ENV UNSLOTH_SKIP_QUANTIZED_MODULES=1
ENV UNSLOTH_DISABLE_QUANTIZATION=1

# 作業ディレクトリを設定
WORKDIR /mnt

# 最終確認
RUN echo "Final environment check:" && \
    python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA available: {torch.cuda.is_available()}, CUDA version: {torch.version.cuda}, GPU count: {torch.cuda.device_count()}')" && \
    echo "Installation complete!"