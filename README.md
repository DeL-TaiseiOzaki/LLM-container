# 🚀 Simple LLM Docker Builder

シンプルで実用的なLLM開発環境を数分で構築するツール

## ✨ 特徴

- **シンプル**: 複雑な設定不要、YAMLファイル1つで完結
- **高速**: uvパッケージマネージャーで高速インストール
- **実用的**: 必要なツールだけを選択してインストール

## 🚀 クイックスタート

### 1. リポジトリをクローン
```bash
git clone https://github.com/yourusername/LLM-container
cd llm-container
```

### 2. 設定ファイルを編集
```yaml
# config.yaml
cuda_version: "12.1"          # あなたのCUDAバージョン
pytorch_version: "2.5.1"       # 省略可能（自動選択）
transformers_version: "4.44.0" # お好みのバージョン

packages:
  vllm: true                   # 必要なものをtrue
  flash_attention2: true
  openai: true
  langchain: true
```

### 3. ビルド＆実行
```bash
# すべて自動で実行
python build.py all

# または個別に実行
python build.py build  # Dockerイメージのビルド
python build.py run    # コンテナの起動
```

## 📦 利用可能なパッケージ

| パッケージ | 説明 | 用途 |
|---------|------|-----|
| **vLLM** | 高速推論エンジン | 本番デプロイ |
| **TRL** | 強化学習ライブラリ | RLHF/DPO訓練 |
| **Unsloth** | 高速ファインチューニング | QLoRA訓練 |
| **DeepSpeed** | 分散学習フレームワーク | 大規模訓練 |
| **Flash Attention 2** | 高速アテンション | メモリ効率改善 |
| **OpenAI** | OpenAI APIクライアント | GPT-4/GPT-3.5連携 |
| **LiteLLM** | 統一APIインターフェース | 複数LLM統合 |
| **LangChain** | LLMアプリ開発 | RAG/エージェント |

## 🎯 サポート環境

### CUDA バージョンとPyTorch対応表

| CUDA | 推奨PyTorch | 利用可能なPyTorch | 推奨GPU |
|------|------------|----------------|---------|
| **11.8** | 2.5.1 | 2.7.0, 2.6.0, 2.5.1, 2.4.1, 2.3.1 | 幅広い互換性（T4, V100, A100） |
| **12.1** | 2.5.1 | 2.5.1, 2.4.1, 2.3.1 | A100, RTX 30xx |
| **12.4** | 2.6.0 | 2.6.0, 2.5.1, 2.4.1 | RTX 40xx |
| **12.6** | 2.7.0 | 2.7.0, 2.6.0 | 最新GPU |
| **12.8** | 2.7.0 | 2.7.0 | H100, H200 |

### Python バージョン
- 3.9, 3.10, 3.11, 3.12

## 💻 使用例

### コンテナに接続
```bash
docker exec -it llm-dev bash
```

### Jupyter Lab起動
```bash
docker exec -it llm-dev jupyter lab --ip 0.0.0.0 --allow-root
# ブラウザで http://localhost:8888 にアクセス
```

### Claude Code使用
```bash
docker exec -it llm-dev claude
```

### Pythonで確認
```python
import torch
import transformers

print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Transformers: {transformers.__version__}")
```

## 🗂️ ファイル構成

```
simple-llm-docker/
├── build.py           # ビルドスクリプト
├── config.yaml        # 設定ファイル
├── templates/
│   └── Dockerfile.j2  # Dockerfileテンプレート
├── requirements.txt   # Python依存
└── README.md         # このファイル
```

## ⚙️ カスタマイズ

### 最小構成（推論のみ）
```yaml
packages:
  vllm: true
  flash_attention2: true
  openai: true
```

### ファインチューニング構成
```yaml
packages:
  trl: true
  unsloth: true
  flash_attention2: true
  deepspeed: true
```

### フルスタック開発
```yaml
packages:
  vllm: true
  langchain: true
  litellm: true
  openai: true
  flash_attention2: true
```

## 🐛 トラブルシューティング

### CUDA バージョンの確認
```bash
nvidia-smi  # ホストマシンで実行
```

### メモリ不足エラー
```bash
# Flash Attentionビルド時のメモリエラー対策
# config.yamlで flash_attention2: false に設定
```

### 既存コンテナの削除
```bash
docker stop llm-dev
docker rm llm-dev
```

## 📝 requirements.txt

```txt
pyyaml>=6.0
jinja2>=3.1.0
```

## 📄 ライセンス

MIT License