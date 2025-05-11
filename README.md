# LLM Docker Environment

LLM開発・推論・ファインチューニング用のDocker環境です。

- **GPU対応** - NVIDIAのCUDA 12.4ベース
- **主要ライブラリ搭載**：PyTorch, Transformers, HuggingFace, LangChain など
- Jupyter LabやFastAPIなど、様々なアプリケーションで利用可能

## 事前準備

1. **Docker** のインストール
2. **NVIDIA Container Toolkit** のインストール（GPU利用時）
   - 確認コマンド: `docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi`

## 利用方法

```bash
# イメージのビルド
docker build -t llm-builder:latest .

# コンテナの起動
docker run --gpus all --rm -itd -v ~/:/mnt --name llm-container -p 8888:8888 llm-builder:latest /bin/bash

# Jupyter Lab起動（コンテナ内で）
jupyter lab --ip 0.0.0.0 --allow-root --no-browser
```

## Flash Attentionのインストール

ベースイメージにはFlash Attentionは含まれていません。必要な場合は以下の方法でインストールできます。

```bash
pip install flash-attn --no-build-isolation
```

## トラブルシューティング

- **ビルドエラー** - ディスク容量不足やネットワーク不安定が原因の可能性
- **GPU検出エラー** - NVIDIA Container Toolkitが正しくインストールされているか確認
- **Flash Attentionエラー** - CUDA環境変数確認 (`export CUDA_HOME=/usr/local/cuda`)

## ライセンス

Apache License 2.0