FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu22.04

# 基本設定
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# システムパッケージ
RUN apt-get update && apt-get install -y \
    curl wget git vim \
    build-essential \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python設定
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# uv（高速パッケージマネージャー）
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"
ENV UV_SYSTEM_PYTHON=1


# Node.js 20 LTS（Claude Code用）
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @anthropic-ai/claude-code \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# PyTorch
RUN uv pip install torch==2.7.0 torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu128

# Transformers（必須）
RUN uv pip install transformers==4.56.0

# 基本MLライブラリ
RUN uv pip install \
    numpy pandas matplotlib seaborn \
    scikit-learn scipy \
    tqdm rich \
    accelerate datasets \
    huggingface-hub tokenizers \
    safetensors sentencepiece \
    ipython

# オプションパッケージ

RUN uv pip install vllm



RUN uv pip install trl peft



RUN uv pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"





RUN uv pip install ninja packaging wheel
RUN MAX_JOBS=4 uv pip install flash-attn --no-build-isolation



RUN uv pip install openai



RUN uv pip install litellm





RUN uv pip install wandb






# 作業ディレクトリ
WORKDIR /workspace

# ユーザー設定（セキュリティ向上）
RUN useradd -m -u 1000 llmuser && \
    chown -R llmuser:llmuser /workspace

# ヘルスチェック
COPY --chown=llmuser:llmuser <<'EOF' /healthcheck.py
import torch
import transformers
import sys

print("=" * 50)
print("🚀 LLM Docker Environment")
print("=" * 50)
print(f"Python: {sys.version.split()[0]}")
print(f"PyTorch: {torch.__version__}")
print(f"Transformers: {transformers.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
print("=" * 50)
EOF

RUN chmod +x /healthcheck.py

# 起動スクリプト
COPY <<'EOF' /entrypoint.sh
#!/bin/bash
python /healthcheck.py


echo "💡 Claude Code: claude"

echo ""
exec "$@"
EOF

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]