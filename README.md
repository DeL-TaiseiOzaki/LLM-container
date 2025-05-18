# LLM Docker Builder

LLM（大規模言語モデル）開発・推論・微調整用のDocker環境を簡単に構築するツール

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/CUDA-11.8%20|%2012.1-green" alt="CUDA 11.8/12.1">
  <img src="https://img.shields.io/badge/PyTorch-2.0%20|%202.1%20|%202.2-red" alt="PyTorch 2.0/2.1/2.2">
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

| プリセット | 説明 |
|------------|------|
| `minimal` | 最小限の構成（基本的なTransformers機能のみ） |
| `standard` | 標準的な開発環境（Transformers, Datasets, JupyterLab等） |
| `full` | 完全な開発環境（HuggingFace全体、最適化ツール、視覚化ツール等） |
| `research` | 研究特化環境（full + 実験・分析ツール） |

## トラブルシューティング

### CUDA関連の問題

- **互換性エラー**: 設定ファイルのCUDAバージョンがホストマシンのドライバーと互換性があるか確認してください
- **bitsandbytesビルドエラー**: ビルド時に `BNB_CUDA_VERSION` が正しく設定されているか確認してください

### PyTorch関連の問題

- **バージョン不一致**: PyTorchとCUDAの互換性を確認（`validate` コマンドを使用）
- **GPUが認識されない**: NVIDIA Container Toolkitが正しくインストールされているか確認

### Flash Attention関連の問題

- **ビルドエラー**: CUDA対応バージョンを確認し、`--no-build-isolation` オプションが指定されているか確認
- **互換性エラー**: PyTorchバージョンとの互換性を検証してください

### Docker関連の問題

- **ビルド失敗**: ディスク容量や権限を確認し、Docker Daemonが実行中か確認してください
- **GPU使用不可**: `--gpus all` オプションが指定されているか、NVIDIA Container Toolkitが正しく設定されているか確認

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