# LLM Docker Builder

LLM（大規模言語モデル）開発・推論・微調整用のDocker環境を簡単に構築するツール

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/CUDA-11.8%20|%2012.1%20|%2012.8-green" alt="CUDA 11.8/12.1/12.8">
  <img src="https://img.shields.io/badge/PyTorch-2.0%20|%202.1%20|%202.7-red" alt="PyTorch 2.0/2.1/2.7">
  <img src="https://img.shields.io/badge/license-Apache%202.0-lightgrey" alt="License">
</div>

## 概要

LLM Docker Builderは、AI開発に必要なDocker環境を簡単に構築するためのツールです。主要コンポーネント（CUDA、PyTorch、Flash Attention、Transformersなど）の互換性を自動検証し、最適なDockerfile構成を生成します。各ライブラリのバージョン間の相互依存関係を考慮し、一貫した環境を提供します。

### 主な特徴

- ✅ **バージョン互換性検証**: CUDA、PyTorch、Flashattention、TRLなどの互換性を自動チェック
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

### インストール手順

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/llm-docker-builder.git
cd llm-docker-builder

# 依存パッケージのインストール
pip install -r requirements.txt

# プロジェクトの初期化
python build.py init
```

## 使い方

### クイックスタート

最も簡単に始めるには、以下のコマンドを実行します：

```bash
# すべての工程（検証、生成、ビルド、実行）を一度に行う
python build.py all --config config.yaml
```

### ステップバイステップ

1. **設定ファイルの作成・編集**

```yaml
# config.yaml
base:
  image: "nvcr.io/nvidia/pytorch"
  tag: "24.05-py3"
  cuda_version: "12.8"
  python_version: "3.10"

gpu:
  architecture: "hopper"  # hopper, ampere, volta, turing など
  count: 2                # GPUの数
  multi_node: false

deep_learning:
  pytorch:
    version: "2.7.0"      # バージョン指定、空文字列("")で最新版
    source: "pip"
    cuda_specific: true
  
  attention:
    flash_attention: true
    xformers: true
    xformers_version: "0.0.30"

libraries:
  use_preset: true
  preset: "full"  # minimal, standard, full, research から選択
```

2. **設定の検証**

```bash
python build.py validate --config config.yaml
```

3. **Dockerfileの生成**

```bash
python build.py generate --config config.yaml --output Dockerfile
```

4. **イメージのビルド**

```bash
python build.py build --config config.yaml --name my-llm-env:latest
```

5. **コンテナの実行**

```bash
python build.py run --image my-llm-env:latest --name my-llm-container
```

## 設定オプション詳細

### 基本設定（`base`）

| オプション | 説明 | 例 |
|------------|------|-----|
| `image` | ベースイメージ | `"nvcr.io/nvidia/pytorch"` |
| `tag` | イメージタグ | `"24.05-py3"` |
| `cuda_version` | CUDAバージョン | `"12.8"`, `"11.8"` |
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
| `pytorch.version` | PyTorchバージョン | `"2.7.0"`, `""` (空文字列で最新版) |
| `attention.flash_attention` | Flash Attention有効化 | `true`, `false` |
| `attention.xformers` | xformers有効化 | `true`, `false` |
| `attention.xformers_version` | xformersバージョン | `"0.0.30"`, `""` (空文字列で最新版) |

### ライブラリ設定（`libraries`）

#### プリセット使用時

```yaml
libraries:
  use_preset: true
  preset: "standard"  # minimal, standard, full, research
```

#### カスタムライブラリ設定

```yaml
libraries:
  use_preset: false
  custom:
    category_name:  # カテゴリ名（任意）
      # バージョン指定あり
      - {"name": "transformers", "version": ">=4.41.0"}
      
      # バージョン指定なし（最新版）
      - {"name": "datasets", "install": true}
      
      # extras指定
      - {"name": "optimum", "install": true, "extra": "[onnxruntime-gpu]"}
      
      # 特殊インストール方法
      - {"name": "flash-attn", "source": "pip install flash-attn --no-build-isolation"}
```

#### ライブラリ定義オプション

| オプション | 説明 | 例 |
|------------|------|-----|
| `name` | パッケージ名 | `"transformers"` |
| `version` | バージョン指定 | `">=4.41.0"`, `"==2.7.0"` |
| `install` | バージョン指定なしでインストール | `true` |
| `extra` | extras指定 | `"[feature]"` |
| `source` | カスタムインストールコマンド | `"pip install ... --extra-index-url ..."` |

#### ライブラリプリセット（`libraries.preset`）

| プリセット | 説明 |
|------------|------|
| `minimal` | 最小限の構成（基本的なTransformers機能のみ） |
| `standard` | 標準的な開発環境（Transformers, Datasets, JupyterLab等） |
| `full` | 完全な開発環境（HuggingFace全体、最適化ツール、視覚化ツール等） |
| `research` | 研究特化環境（full + 実験・分析ツール） |

### 環境変数設定（`environment`）

```yaml
environment:
  preset:
    hopper: true
    multi_gpu: true
  
  custom:
    - {"name": "PYTORCH_CUDA_ALLOC_CONF", "value": "max_split_size_mb:512"}
    - {"name": "NCCL_DEBUG", "value": "INFO"}
```

## 設定ファイル例

### LoRA微調整用設定例

```yaml
base:
  image: "nvcr.io/nvidia/pytorch"
  tag: "24.05-py3"
  cuda_version: "12.8"
  python_version: "3.10"

gpu:
  architecture: "hopper"
  count: 4
  multi_node: false

deep_learning:
  pytorch:
    version: ""  # 空文字列で最新バージョン自動選択
    source: "pip"
    cuda_specific: true
  
  attention:
    flash_attention: true  # バージョン指定なしで最適化インストール
    xformers: true
    xformers_version: "0.0.30"
    triton: true

libraries:
  use_preset: false
  custom:
    lora:
      - {"name": "transformers", "version": ">=4.41.0"}
      - {"name": "peft", "version": ">=0.10.0"}
      - {"name": "accelerate", "version": ">=0.29.3"}
      - {"name": "deepspeed", "install": true}  # バージョン指定なし
      - {"name": "trl", "version": ">=0.10.0"}
      - {"name": "ninja", "install": true}
    
    data:
      - {"name": "datasets", "install": true}
      - {"name": "huggingface_hub", "install": true}
      - {"name": "sentencepiece", "install": true}
      
    utils:
      - {"name": "flash-attn", "source": "pip install flash-attn --no-build-isolation"}
      - {"name": "wandb", "install": true}
      - {"name": "jupyterlab", "install": true}
```

### 研究環境用設定例

```yaml
base:
  image: "nvcr.io/nvidia/pytorch"
  tag: "24.05-py3"
  cuda_version: "12.8"
  python_version: "3.10"

gpu:
  architecture: "ampere"  # RTX 3090など
  count: 2

deep_learning:
  pytorch:
    version: "2.7.0"  # 特定バージョン指定
  
  attention:
    flash_attention: true
    flash_attention_version: "2.7.4.post1"  # 特定バージョン指定

libraries:
  use_preset: true
  preset: "research"  # 研究特化プリセット使用
```

## トラブルシューティング

### バージョン関連の問題

- **空バージョン文字列エラー**: ライブラリ定義で `"version": ""` と空文字列を指定した場合、代わりに `"install": true` を使用してください。
  
  ```yaml
  # NG
  - {"name": "package", "version": ""}
  
  # OK
  - {"name": "package", "install": true}
  ```

- **バージョン指定構文エラー**: パッケージバージョン指定には、`==`, `>=`, `<=`, `~=` などの演算子を使用できます。
  
  ```yaml
  # 特定バージョン
  - {"name": "transformers", "version": "==4.41.0"}
  
  # 最小バージョン
  - {"name": "peft", "version": ">=0.10.0"}
  ```

### CUDA関連の問題

- **互換性エラー**: 設定ファイルのCUDAバージョンがホストマシンのドライバーと互換性があるか確認してください。
  
  ```bash
  # ドライバーバージョン確認
  nvidia-smi
  ```

- **Flash Attentionビルドエラー**: Flash Attentionのビルドにはビルドツールが必要です。特殊なインストール方法を使用してください。
  
  ```yaml
  - {"name": "flash-attn", "source": "pip install flash-attn --no-build-isolation"}
  ```

### Docker関連の問題

- **ビルド失敗**: ディスク容量や権限を確認し、Docker Daemonが実行中か確認してください。
  
  ```bash
  # Docker状態確認
  sudo systemctl status docker
  ```

- **GPU使用不可**: `--gpus all` オプションが指定されているか、NVIDIA Container Toolkitが正しく設定されているか確認。
  
  ```bash
  # テスト
  docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
  ```

## 開発ロードマップ

- [ ] Web UIインターフェースの追加
- [ ] より多くのライブラリの互換性マップの追加
- [ ] マルチノード分散学習の設定強化
- [ ] CI/CDパイプラインの統合
- [ ] テストスイートの追加

## ライセンス

Apache License 2.0

## 貢献方法

貢献は歓迎します！以下の方法で参加できます：

1. Issueを開く（バグレポート、機能リクエストなど）
2. プルリクエストを送信（バグ修正、新機能追加など）
3. ドキュメントの改善

---

**注意**: このツールは開発中であり、すべての機能や互換性が完全に保証されるわけではありません。本番環境での使用には十分なテストを行ってください。