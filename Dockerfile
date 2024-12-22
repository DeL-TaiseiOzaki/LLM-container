# .devcontainer/Dockerfile

# NVIDIA CUDA ベースで Ubuntu 22.04 を利用（タグは必要に応じて適宜変更可能）
FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# OS パッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Mambaforge (Miniforge) のインストール
ENV MAMBAFORGE_VERSION=23.5.0-0
RUN curl -LO https://github.com/conda-forge/miniforge/releases/download/${MAMBAFORGE_VERSION}/Mambaforge-${MAMBAFORGE_VERSION}-Linux-x86_64.sh \
    && bash Mambaforge-${MAMBAFORGE_VERSION}-Linux-x86_64.sh -b -p /opt/conda \
    && rm Mambaforge-${MAMBAFORGE_VERSION}-Linux-x86_64.sh

# conda/mamba コマンドを PATH に通す
ENV PATH /opt/conda/bin:$PATH

# PyTorch + CUDA + 主要ライブラリをインストール
RUN mamba install -y \
    python=3.10 \
    pytorch \
    torchvision \
    torchaudio \
    pytorch-cuda=12.4 \
    -c pytorch -c nvidia \
    transformers \
    sentencepiece \
    accelerate \
    datasets \
    jupyterlab \
    ipywidgets \
    && mamba clean -yaf

# flashattention, vllm, deepspeed などをpipでインストール
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        flash-attn \
        vllm \
        deepspeed

# 作業ディレクトリを設定
WORKDIR /workspace
