# .devcontainer/Dockerfile

# NVIDIA CUDA ベースで Ubuntu 22.04 を利用（タグは必要に応じて適宜変更可能）
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

# PyTorch + CUDA + 主要ライブラリをインストール
RUN mamba install -y \
    python=3.11 \
    transformers \
    sentencepiece \
    accelerate \
    trl \
    peft \
    datasets \
    numpy \
    pandas \ 
    matplotlib \
    scipy \
    scikit-learn \
    wandb \
    bitsandbytes \
    jupyterlab \
    ipywidgets \
    && mamba clean -yaf

# PyTorch + CUDAをpipでインストール
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        torch \
        torchvision \
        torchaudio \
        --index-url https://download.pytorch.org/whl/cu124

# flashattention, vllm, deepspeed などをpipでインストール
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        flash-attn \
        vllm \
        deepspeed \
        openai \
        anthropic

# 作業ディレクトリを設定
WORKDIR /mnt
