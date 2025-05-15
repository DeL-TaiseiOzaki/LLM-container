# --------------------------------------------------------------------------------
# .devcontainer/Dockerfile
# --------------------------------------------------------------------------------
# ベースイメージを変更 - NVIDIA公式のPyTorchコンテナを使用
FROM nvcr.io/nvidia/pytorch:24.05-py3

# あるいは現在のベースイメージを維持し、必要なツールを明示的にインストール
FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

# OS パッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL \
  https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
  -o /tmp/miniforge.sh \
  && bash /tmp/miniforge.sh -b -p /opt/conda \
  && rm /tmp/miniforge.sh

# conda/mamba コマンドを PATH に通す
ENV PATH=/opt/conda/bin:$PATH

ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# 環境変数の設定も修正（警告の解消）
ENV PYTHONUNBUFFERED=1

# --------------------------------------------------------------------------------
# 1. conda (mamba) 経由で基本ライブラリ + LLM 主要ライブラリをインストール
# --------------------------------------------------------------------------------
RUN mamba install -y -c conda-forge \
    python=3.11 \
    transformers \
    sentencepiece \
    accelerate \
    trl=0.12.0 \
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
    unsloth \
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
# 基本的なライブラリを先にインストール
RUN pip install --no-cache-dir \
        openai \
        anthropic \
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
        pre-commit \
        ninja \
        packaging \
        wheel \
        setuptools


# CUDA依存ライブラリを個別にインストール
RUN pip install --no-cache-dir \
        vllm \
        deepspeed \
        xformers

# 作業ディレクトリを設定
WORKDIR /mnt