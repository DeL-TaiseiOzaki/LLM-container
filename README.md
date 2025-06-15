# LLM Docker Builder

LLM（大規模言語モデル）開発・推論・微調整用のDocker環境を簡単に構築するツール

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/CUDA-11.8%20|%2012.1-green" alt="CUDA 11.8/12.1">
  <img src="https://img.shields.io/badge/PyTorch-2.0%20|%202.1%20|%202.2-red" alt="PyTorch 2.0/2.1/2.2">
  <img src="https://img.shields.io/badge/Package%20Manager-uv-purple" alt="uv">
  <img src="https://img.shields.io/badge/license-Apache%202.0-lightgrey" alt="License">
</div>

## 概要

LLM Docker Builderは、AI開発に必要なDocker環境を簡単に構築するためのツールです。主要コンポーネント（CUDA、PyTorch、Flash Attention、Transformersなど）の互換性を自動検証し、最適なDockerfile構成を生成します。

### 主な特徴

- ✅ **バージョン互換性検証**: CUDA、PyTorch、Flash Attention、TRLなどの互換性を自動チェック
- ✅ **超高速パッケージ管理**: uvを使用してpipの10-100倍高速なインストール
- ✅ **マルチGPU/マルチノード対応**: 複数GPU環境の最適な設定を自動生成
- ✅ **Claude Code対応**: Anthropicの開発支援AIツールを統合
- ✅ **プリセット設定**: 研究、本番環境など用途別の最適な構成を提供
- ✅ **カスタマイズ**: 詳細な設定オプションによる柔軟な環境構築
- ✅ **簡単な操作**: 単一コマンドで全プロセス（生成・ビルド・実行）を完了

## インストールと準備

### 必要条件

- Python 3.8以上
- Docker
- NVIDIA Container Toolkit（GPU利用時）
- Git
- Make（オプション）

### インストール手順

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/llm-docker-builder.git
cd llm-docker-builder

# 依存パッケージのインストール
pip install -r requirements.txt

# プロジェクトの初期化
python build.py init
# または
make init
```

## 使い方

### クイックスタート

最も簡単に始めるには、以下のコマンドを実行します：

```bash
# すべての工程（検証、生成、ビルド、実行）を一度に行う
python build.py all --config config.yaml

# またはMakefileを使用
make all
```

### Docker Composeを使用する場合

```bash
# docker-compose.ymlが生成されているので
docker-compose up -d
```

### ステップバイステップ

1. **設定ファイルの作成・編集**

```yaml
# config.yaml
base:
  image: "nvcr.io/nvidia/pytorch"
  tag: "24.05-py3"
  cuda_version: "12.1"
  python_version: "3.10"

gpu:
  architecture: "hopper"  # hopper, ampere, volta, turing など
  count: 2                # GPUの数
  multi_node: false

deep_learning:
  pytorch:
    version: "2.2.0"
  
  attention:
    flash_attention: true
    flash_attention_version: "2.3.3"

claude_code:
  install: true
  nodejs_version: "lts"  # lts, latest, または特定のバージョン

libraries:
  use_preset: true
  preset: "full"  # minimal, standard, full, research から選択
```

2. **設定の検証**

```bash
python build.py validate --config config.yaml
# または
make validate
```

3. **Dockerfileの生成**

```bash
python build.py generate --config config.yaml --output Dockerfile
# または
make generate
```

4. **イメージのビルド**

```bash
python build.py build --config config.yaml --name my-llm-env:latest
# または
make build IMAGE_NAME=my-llm-env:latest
```

5. **コンテナの実行**

```bash
python build.py run --image my-llm-env:latest --name my-llm-container
# または
make run
```

## uvによる高速化

このツールは[uv](https://github.com/astral-sh/uv)を使用してPythonパッケージを管理します。uvの利点：

- **超高速インストール**: pipの10-100倍高速
- **並列処理**: 複数パッケージを同時にダウンロード・インストール
- **効率的なキャッシュ**: 再ビルド時の時間を大幅短縮
- **pip互換**: 既存のrequirements.txtがそのまま使用可能
- **スマートな依存解決**: より効率的な依存関係の解決

## 設定オプション詳細

### 基本設定（`base`）

| オプション | 説明 | 例 |
|------------|------|-----|
| `image` | ベースイメージ | `"nvcr.io/nvidia/pytorch"` |
| `tag` | イメージタグ | `"24.05-py3"` |
| `cuda_version` | CUDAバージョン | `"12.1"`, `"11.8"` |
| `python_version` | Pythonバージョン | `"3.10"`, `"3.11"` |

### GPU設定（`gpu`）

| オプション | 説明 | 例 |
|------------|------|-----|
| `architecture` | GPUアーキテクチャ | `"hopper"`, `"ampere"`, `"volta"` |
| `count` | GPU数 | `1`, `4`, `8` |
| `multi_node` | マルチノード有効化 | `true`, `false` |
| `nodes` | ノード数 | `2`, `4` |

### 深層学習設定（`deep_learning`）

| オプション | 説明 | 例 |
|------------|------|-----|
| `pytorch.version` | PyTorchバージョン | `"2.2.0"`, `"2.0.0"` |
| `attention.flash_attention` | Flash Attention有効化 | `true`, `false` |
| `attention.flash_attention_version` | Flash Attentionバージョン | `"2.3.3"` |
| `attention.xformers` | xformers有効化 | `true`, `false` |

### ライブラリプリセット（`libraries`）

| プリセット | 説明 | 主な内容 |
|------------|------|----------|
| `minimal` | 最小限の構成 | Transformers、NumPy、Pandas、Matplotlib |
| `standard` | 標準的な開発環境 | minimal + Accelerate、PEFT、Datasets、JupyterLab |
| `full` | 完全な開発環境 | standard + TRL、LangChain、DeepSpeed、WandB、開発ツール |
| `research` | 研究特化環境 | full + PyTorch Lightning、Optuna、MLflow、実験ツール |

## 生成されるファイル

- `Dockerfile`: カスタマイズされたDockerfile
- `docker-compose.yml`: Docker Compose設定ファイル
- `.dockerignore`: Docker ビルドの除外ファイル設定
- `Makefile`: 便利なコマンドショートカット

## トラブルシューティング

### uvインストールの問題

- **curlが見つからない**: `apt-get install curl` を実行
- **uvのインストールに失敗**: ネットワーク接続を確認

### CUDA関連の問題

- **互換性エラー**: 設定ファイルのCUDAバージョンがホストマシンのドライバーと互換性があるか確認
- **GPUが認識されない**: NVIDIA Container Toolkitが正しくインストールされているか確認

### PyTorch関連の問題

- **バージョン不一致**: PyTorchとCUDAの互換性を確認（`validate` コマンドを使用）
- **メモリ不足**: Docker Desktopのメモリ制限を確認（最低16GB推奨）

### Flash Attention関連の問題

- **ビルドエラー**: CUDA対応バージョンとGPUアーキテクチャを確認
- **互換性エラー**: PyTorchバージョンとの互換性を検証

### Docker関連の問題

- **ビルド失敗**: ディスク容量（最低50GB推奨）や権限を確認
- **キャッシュの問題**: `docker builder prune` でビルドキャッシュをクリア

## パフォーマンスのヒント

1. **Docker BuildKitを有効化**:
   ```bash
   export DOCKER_BUILDKIT=1
   ```

2. **uvキャッシュの永続化**: docker-compose.ymlのボリューム設定を使用

3. **並列ビルドの活用**: 
   ```bash
   docker build --build-arg MAX_JOBS=$(nproc) .
   ```

## ライセンス

Apache License 2.0

## 貢献方法

貢献は歓迎します！以下の方法で参加できます：

1. Issueを開く（バグレポート、機能リクエストなど）
2. プルリクエストを送信（バグ修正、新機能追加など）
3. ドキュメントの改善
4. 互換性マップの更新・追加

### 開発環境のセットアップ

```bash
# 開発用の仮想環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 開発用依存関係をインストール
pip install -r requirements-dev.txt

# pre-commitフックをセットアップ
pre-commit install
```

---

**注意**: このツールは開発中であり、すべての機能や互換性が完全に保証されるわけではありません。本番環境での使用には十分なテストを行ってください。

**パフォーマンス**: uvを使用することで、通常のpipベースのDockerビルドと比較して、パッケージインストール時間を最大90%短縮できます。
```

主な変更点：
1. uvに関する説明を追加
2. パフォーマンスのヒントセクションを追加
3. Docker Composeの使用方法を追加
4. Makefileの使用例を追加
5. 生成されるファイルのセクションを追加
6. uvの利点を強調
7. トラブルシューティングにuv関連の項目を追加