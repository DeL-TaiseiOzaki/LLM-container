# LLM Container

マルチユーザー対応の LLM 開発用 Docker 環境。
`config.yaml` でパッケージを選択し、Jinja2 テンプレートから Dockerfile を自動生成してビルドする。

## クイックスタート

```bash
# 1. 初期設定（初回のみ。ホストの CUDA バージョンを自動検出）
uv run build.py init

# 2. config.yaml を編集（パッケージの ON/OFF など）

# 3. ビルド（初回は 10-20 分）
make build

# 4. 起動
make run

# 5. 接続
make exec
```

## リポジトリ構成

```
.
├── build.py                  # ビルドスクリプト（検証・Dockerfile 生成・ビルド）
├── config.yaml               # 環境設定（CUDA/Python/パッケージ選択）
├── docker-compose.yml        # Docker Compose 定義
├── run.sh                    # コンテナ起動スクリプト（sudo 自動判定）
├── Makefile                  # ショートカットコマンド
├── templates/
│   └── Dockerfile.j2         # Dockerfile の Jinja2 テンプレート
├── setup/
│   ├── q                     # GPU Task Spooler ラッパースクリプト
│   └── ts-shared.service     # systemd サービス定義
├── GPU-QUEUE.md              # GPU キューの使い方ガイド
├── SETUP-GPU-QUEUE.md        # GPU キューのセットアップ手順
└── apply-ts-to-containers.sh # 既存コンテナへの GPU キュー適用スクリプト
```

## 含まれるもの

`config.yaml` の `packages` セクションで ON/OFF を切り替え可能。

| カテゴリ | パッケージ | デフォルト |
|---------|-----------|-----------|
| **基本** | PyTorch, Transformers, NumPy, Pandas, Matplotlib, scikit-learn, SciPy | 常時 |
| **推論** | vLLM, Flash Attention 2, bitsandbytes | ON |
| **学習** | TRL, Unsloth, PEFT | ON |
| **API** | OpenAI, LiteLLM | ON |
| **トークナイザ** | SentencePiece, Tokenizers | ON |
| **実験管理** | Weights & Biases | ON |
| **分散学習** | DeepSpeed | OFF |
| **その他** | LangChain, MLflow, TensorBoard | OFF |
| **開発ツール** | Claude Code (Node.js 20 LTS), Jupyter Lab | Code: ON / Jupyter: OFF |

パッケージマネージャーは **uv** を使用。コンテナ内でも `uv pip install` で追加インストールできる。

## マルチユーザー利用

ユーザーごとに独立したコンテナ・ワークスペースが作られる。

```bash
# ozaki さん用
make run USER=ozaki BASE_DIR=/home/ozaki

# yamada さん用
make run USER=yamada BASE_DIR=/home/yamada
```

コンテナ名は `llm-<USER>` になる（例: `llm-ozaki`）。

## GPU キュー（Task Spooler）

複数ユーザーで GPU を共有するための **ジョブキューシステム**。
`q` コマンドでジョブを投げると、空き GPU に自動で割り当てられる。

```bash
# GPU 1 枚でジョブを実行
q -G 1 python train.py

# GPU 2 枚で実行
q -G 2 python pretrain.py

# キューの状態を確認
q
```

- 空き GPU があればすぐ実行、なければ自動で待機
- ターミナルを閉じてもジョブは継続（setsid で切り離し）
- `CUDA_VISIBLE_DEVICES` の手動設定は不要
- ジョブのログは `/cache/ts-queue/logs/` に自動保存

詳細は [GPU-QUEUE.md](GPU-QUEUE.md) を参照。セットアップ手順は [SETUP-GPU-QUEUE.md](SETUP-GPU-QUEUE.md) を参照。

## カスタマイズ

### パッケージの選択

`config.yaml` を編集：

```yaml
cuda_version: "12.8"        # 11.8, 12.1, 12.4, 12.6, 12.8
python_version: "3.11"      # 3.9, 3.10, 3.11, 3.12
pytorch_version: "2.7.0"    # CUDA バージョンに応じた互換版を自動選択可

packages:
  vllm: true          # 高速推論
  unsloth: false       # ← false にすれば無効化
  wandb: true          # 実験管理
```

### ベースイメージの変更

`templates/Dockerfile.j2` の 1 行目を編集：

```dockerfile
FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu22.04  # ← お好きなイメージに
```

### build.py のコマンド一覧

```bash
uv run build.py init       # config.yaml を生成（CUDA 自動検出）
uv run build.py validate   # 設定の検証
uv run build.py generate   # Dockerfile を生成
uv run build.py build      # 検証 → 生成 → ビルド
uv run build.py run        # コンテナ起動
uv run build.py list       # 有効パッケージ一覧
uv run build.py all        # 全工程を一括実行
```

## ボリュームマッピング

例：`make run USER=ozaki BASE_DIR=/home/ozaki` で起動した場合

| ホスト側 | コンテナ内 | 用途 |
|---------|-----------|------|
| `/home/ozaki/workspace` | `/workspace` | 作業ディレクトリ |
| `/home/ozaki/models` | `/models` | モデル保存 |
| `/home/ozaki/datasets` | `/datasets` | データセット |
| `/home/ozaki/logs` | `/logs` | ログ |

### 共有キャッシュ

全ユーザーで共有され、ディスク容量を節約する。

| ホスト側 | コンテナ内 | 用途 |
|---------|-----------|------|
| `/data/cache/huggingface` | `/cache/huggingface` | HuggingFace モデル・データセット |
| `/data/cache/uv` | `/cache/uv` | uv パッケージキャッシュ |
| `/data/cache/torch` | `/cache/torch` | PyTorch Hub キャッシュ |
| `/data/cache/matplotlib` | `/cache/matplotlib` | Matplotlib 設定 |
| `/data/cache/ts-queue` | `/cache/ts-queue` | GPU キューのソケット・ログ |

## 環境変数

以下の環境変数がホストから自動的にコンテナに渡される。起動前にホスト側で `export` しておくこと。

| 変数名 | 用途 |
|--------|------|
| `ANTHROPIC_API_KEY` | Claude API |
| `OPENAI_API_KEY` | OpenAI API |
| `HF_TOKEN` | Hugging Face Hub |

## Make コマンド一覧

```bash
make build   # イメージビルド
make run     # コンテナ起動
make exec    # コンテナに接続
make stop    # コンテナ停止
make logs    # ログ表示
make clean   # コンテナ削除
make down    # docker compose down
```

## トラブルシューティング

### Docker 権限エラー

```bash
# 解決法 1: run.sh を使う（sudo 自動判定）
./run.sh <ユーザー名>

# 解決法 2: docker グループに追加
sudo usermod -aG docker $USER
# ログアウト → 再ログイン
```

### CUDA バージョンが合わない

`config.yaml` の `cuda_version` をホストに合わせて変更：

```yaml
cuda_version: "12.8"   # nvidia-smi で確認した値に合わせる
```

`uv run build.py init` を使えばホストの CUDA バージョンを自動検出して `config.yaml` を生成する。

### GPU キューが動かない

```bash
# ソケットの存在確認
ls -la /cache/ts-queue/.socket

# ホスト側でサービスの状態確認
sudo systemctl status ts-shared
```

詳細は [SETUP-GPU-QUEUE.md](SETUP-GPU-QUEUE.md) のトラブルシューティングを参照。

## ライセンス

Apache License 2.0
