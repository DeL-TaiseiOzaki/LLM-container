# --------------------------------------------------------------------------------
# .devcontainer/Dockerfile
# --------------------------------------------------------------------------------

# NVIDIA CUDA ベースで Ubuntu 22.04 を利用（タグは必要に応じて変更可能）
FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

# OS パッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Mambaforge (Miniforge) のインストール
ENV MAMBAFORGE_VERSION=latest
RUN curl -fsSL \
  https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh \
  -o /tmp/mambaforge.sh \
  && bash /tmp/mambaforge.sh -b -p /opt/conda \
  && rm /tmp/mambaforge.sh

# conda/mamba コマンドを PATH に通す
ENV PATH /opt/conda/bin:$PATH
# Python でバッファリングが発生しないように (ログがすぐ表示される)
ENV PYTHONUNBUFFERED=1

# --------------------------------------------------------------------------------
# 1. conda (mamba) 経由で基本ライブラリ + LLM 主要ライブラリをインストール
# --------------------------------------------------------------------------------
RUN mamba install -y -c conda-forge \
    python=3.11 \
    transformers \
    sentencepiece \
    accelerate \
    trl \
    peft \
    bitsandbytes \
    datasets \
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
    && mamba clean -yaf

# --------------------------------------------------------------------------------
# 2. PyTorch + CUDA を公式ホイールから pip でインストール
#    （pytorch.org の "cu124" ホイールを利用）
# --------------------------------------------------------------------------------
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        torch \
        torchvision \
        torchaudio \
        --index-url https://download.pytorch.org/whl/cu124

# --------------------------------------------------------------------------------
# 3. pip で追加ライブラリ (flash-attn, vllm, deepspeed, etc.) をまとめてインストール
# --------------------------------------------------------------------------------
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        flash-attn \
        vllm \
        deepspeed \
        openai \
        anthropic \
        xformers \
        evaluate \
        huggingface_hub \
        "optimum[onnxruntime-gpu]" \
        langchain \
        llama_index \
        "ray[default]" \
        black \
        flake8 \
        isort \
        mypy \
        pre-commit

# --------------------------------------------------------------------------------
# 作業ディレクトリを設定
# --------------------------------------------------------------------------------
WORKDIR /mnt
