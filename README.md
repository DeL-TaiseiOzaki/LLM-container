# 🚀 Simple LLM Docker Builder

LLM開発環境を数分で構築できる、シンプルで実用的なDockerビルダー

## ✨ 特徴

- **🎯 シンプル**: YAMLファイル1つで設定完了
- **⚡ 高速**: uvパッケージマネージャーによる高速インストール  
- **🔧 柔軟**: 必要なツールだけを選択可能
- **🤖 Claude Code対応**: AI開発支援ツール統合
- **📊 MLOps対応**: Weights & Biases、MLflow統合可能

## 🚀 クイックスタート（3分で環境構築）

```bash
# 1. リポジトリをクローン
git clone https://github.com/yourusername/simple-llm-docker.git
cd simple-llm-docker

# 2. 初期設定（CUDAバージョン自動検出）
make init

# 3. 必要に応じてconfig.yamlを編集

# 4. ビルド＆起動
make all

# 5. コンテナに接続
make exec
```

これだけで、PyTorch + Transformers + vLLM環境が立ち上がります！

## 📦 インストールされるもの

### 基本パッケージ（常にインストール）
- PyTorch（CUDAバージョンに最適化）
- Transformers
- NumPy, Pandas, Matplotlib
- Accelerate, Datasets
- Hugging Face Hub

### オプションパッケージ（config.yamlで選択）

| カテゴリ | パッケージ | 説明 | 用途 |
|---------|----------|------|-----|
| **推論** | vLLM | PagedAttention高速推論 | 本番デプロイ |
| **学習** | TRL | 強化学習（RLHF/DPO） | アライメント |
|  | Unsloth | 2倍速ファインチューニング | QLoRA学習 |
|  | DeepSpeed | 分散学習フレームワーク | 大規模学習 |
|  | Flash Attention 2 | メモリ効率改善 | 長文処理 |
| **API** | OpenAI | GPT-4/GPT-3.5連携 | API統合 |
|  | LiteLLM | 統一APIインターフェース | マルチLLM |
|  | LangChain | LLMアプリ開発 | RAG/Agent |
| **MLOps** | Weights & Biases | 実験管理・追跡 | 実験記録 |
|  | MLflow | モデル管理 | バージョン管理 |
| **開発** | Claude Code | AI開発支援 | コード生成 |
|  | Jupyter Lab | ノートブック環境 | 実験・分析 |

## 📝 使い方

### 基本コマンド

```bash
make init      # 初期設定（初回のみ）
make build     # イメージビルド
make run       # コンテナ起動
make exec      # コンテナ接続
make stop      # コンテナ停止
make logs      # ログ表示
make clean     # クリーンアップ
```

### config.yaml の編集

```yaml
# 基本設定
cuda_version: "12.1"        # あなたのGPUに合わせて変更
python_version: "3.11"      # 3.9〜3.12から選択

# パッケージ選択（true/falseで切り替え）
packages:
  vllm: true               # 高速推論が必要なら
  flash_attention2: true   # メモリ効率を重視するなら
  openai: true            # OpenAI API使うなら
  wandb: false            # 実験管理が必要なら
  # ... 他のパッケージも同様に
```

### 構成例

**最小構成（推論のみ）**
```yaml
packages:
  vllm: true
  openai: true
```

**ファインチューニング構成**
```yaml
packages:
  trl: true
  unsloth: true
  flash_attention2: true
  wandb: true
```

**フルスタック開発**
```yaml
packages:
  vllm: true
  langchain: true
  openai: true
  mlflow: true
```

## 🔧 カスタマイズ

### ベースイメージの変更

`templates/Dockerfile.j2` の最初の行を編集することで、ベースイメージを自由に変更できます：

```dockerfile

# 例1: PyTorch公式イメージを使用
FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-runtime

# 例2: nvidia公式イメージを使用
FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu22.04

# 例3: CPU専用（GPU不要の場合）
FROM ubuntu:22.04
```

**注意事項**：
- CUDAバージョンは `config.yaml` の `cuda_version` で制御されます
- Ubuntu 22.04ベースを推奨（依存関係の互換性）
- 変更後は `make build` で再ビルドが必要です

### 環境変数の設定

`docker-compose.yml` で環境変数を管理：

```yaml
environment:
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
  - OPENAI_API_KEY=${OPENAI_API_KEY}
  - HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}
```

`.env` ファイルを作成して自動読み込み：
```bash
echo "OPENAI_API_KEY=sk-xxx" >> .env
echo "HF_TOKEN=hf_xxx" >> .env
```

## 🎯 CUDA-PyTorchバージョン対応表

| CUDA | 推奨PyTorch | その他利用可能 | 推奨GPU |
|------|------------|-------------|---------|
| **11.8** | 2.5.1 | 2.3.1〜2.7.0 | 幅広い互換性 |
| **12.1** | 2.5.1 | 2.3.1〜2.5.1 | RTX 30xx/A100 |
| **12.4** | 2.6.0 | 2.4.1〜2.6.0 | RTX 40xx |
| **12.8** | 2.7.0 | 2.7.0のみ | H100/H200 |

CUDAバージョンの確認：
```bash
nvidia-smi  # "CUDA Version: XX.X" を確認
```

## 🐛 トラブルシューティング

### よくある問題と解決策

**Q: CUDAバージョンがわからない**
```bash
nvidia-smi | grep "CUDA Version"
# または
make init  # 自動検出されます
```

**Q: メモリ不足エラー（Flash Attentionビルド時）**
```yaml
# config.yaml で無効化
packages:
  flash_attention2: false
```

**Q: 既存のコンテナと競合する**
```bash
make clean  # 既存環境をクリーンアップ
make all    # 再構築
```

**Q: GPUが認識されない**
```bash
# Docker内で確認
docker exec -it llm-dev nvidia-smi

# NVIDIA Container Toolkitの再インストール
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## 📊 パフォーマンス目安

| 構成 | イメージサイズ | ビルド時間 | 用途 |
|-----|--------------|-----------|-----|
| 最小構成 | 約8GB | 5-10分 | 推論のみ |
| 標準構成 | 約12GB | 10-15分 | 開発・実験 |
| フル構成 | 約18GB | 15-20分 | 全機能 |

## 📁 ファイル構成

```
simple-llm-docker/
├── build.py               # ビルドスクリプト
├── config.yaml           # 設定ファイル
├── docker-compose.yaml    # Docker Compose設定
├── templates/
│   └── Dockerfile.j2     # Dockerfileテンプレート
├── workspace/            # 作業ディレクトリ（自動作成）
├── Makefile             # 便利コマンド
├── requirements.txt     # Python依存
└── README.md           # このファイル
```

## 📄 ライセンス

Apache License 2.0
