# LLM Docker Environment

本リポジトリでは、**LLM（Large Language Model）の開発・推論・ファインチューニング**、および**エージェントシステム構築**に適した Docker イメージを作成・共有しています。  

- **GPU 対応**（NVIDIA Container Toolkit 必須）  
- **Jupyter Lab** だけでなく、**任意のアプリケーションやフレームワーク**（FastAPI, Flask, CLI ツール等）で利用可能  
- 主なライブラリ:
  - Python + Mambaforge (Miniforge)
  - PyTorch + CUDA
  - Transformers, Accelerate, Datasets, Sentencepiece
  - flash-attention, vllm, deepspeed など

Docker コンテナとして環境をまとめることで、クラウドやオンプレ、ローカルマシンなど、どこでも同じ状態を再現でき、LLM の実験・サービス開発を効率化できます。

---

## 目次

1. [特徴](#特徴)  
2. [事前準備](#事前準備)  
3. [ビルド方法](#ビルド方法)  
4. [利用方法](#利用方法)  
   - 4.1 [コンテナ内で Jupyter Lab を起動](#コンテナ内で-jupyter-lab-を起動)  
   - 4.2 [CLI / FastAPI / その他アプリケーション](#cli--fastapi--その他アプリケーション)  
5. [ディレクトリ構成](#ディレクトリ構成)  
6. [トラブルシューティング](#トラブルシューティング)  
7. [ライセンス](#ライセンス)

---

## 特徴

- **Python 3.10 + Mambaforge**  
  - 柔軟に Python パッケージを管理でき、依存関係を簡潔に保持  
- **PyTorch + CUDA 12.2**  
  - GPU を活用した高速な推論・学習（NVIDIA GPU）  
- **flash-attention**  
  - 大規模言語モデルの推論・学習を高速化  
- **vllm**  
  - 高スループットなモデル推論が可能  
- **deepspeed**  
  - 大規模モデルの分散トレーニング・メモリ最適化  
- **Hugging Face Transformers / Accelerate / Datasets / Sentencepiece**  
  - 最新の LLM フレームワークやトークナイザーを活用  
- **Jupyter Lab / ipywidgets**  
  - Notebook ベースの開発にも対応（ただし必須ではなく、任意のアプリケーションを使えます）

---

## 事前準備

1. **Docker** がインストールされていること  
   - [Docker Desktop](https://www.docker.com/products/docker-desktop) または [Docker Engine](https://docs.docker.com/engine/install/)  
   - `docker version` で動作確認
2. **NVIDIA Container Toolkit** がインストールされていること (GPU 利用する場合)  
   - [公式ドキュメント](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) を参考にセットアップ  
   - セットアップ後、下記コマンドが正常に実行できれば OK  
     ```bash
     docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
     ```

---

## ビルド方法

**1. リポジトリをクローン**

```bash
git clone <このリポジトリのURL>
cd <クローンしたディレクトリ>
```

**2. Docker イメージをビルド**

```bash
docker build -t my-llm-image:latest -f .devcontainer/Dockerfile .
```

- `my-llm-image:latest` はイメージに付けるタグ名（任意）  
- `.devcontainer/Dockerfile` はビルド用 Dockerfile のパス。変更している場合は適宜修正  

ビルド途中、通信速度・ストレージ不足等で失敗する可能性があります。何度かリトライするか、通信環境やディスク容量を見直してください。

---

## 利用方法

### 1. コンテナを起動

GPU を使う場合の例（NVIDIA Container Toolkit が必須）:
```bash
docker run --gpus all --rm -it \
  -p 8888:8888 \
  my-llm-image:latest \
  /bin/bash
```

- `--gpus all`: GPU をすべて利用  
- `-p 8888:8888`: ポートをコンテナ外にフォワード（任意のアプリケーションで活用可能）  
- `/bin/bash`: シェルに入る。アプリ直接起動したい場合はコマンドを置き換えてください。

### 2. コンテナ内で Jupyter Lab を起動

任意で、Notebook ベースの開発を行いたい場合:
```bash
jupyter lab --ip 0.0.0.0 --allow-root --no-browser
```
これにより、ホスト側ブラウザから [http://localhost:8888](http://localhost:8888) へアクセスすれば Jupyter Lab を使用できます（ログに表示されるトークンや URL を使用）。

### 3. CLI / FastAPI / その他アプリケーション

Notebook 以外にも、コンテナ内で自由にコマンドを実行できます。
```bash
# 例: Python スクリプトを実行
python scripts/my_llm_script.py

# 例: FastAPI アプリを起動
uvicorn my_app:app --host 0.0.0.0 --port 8080
```
ポート番号を変えた場合は、起動オプションの `-p 8080:8080` なども合わせて変更してください。

---

## ディレクトリ構成

```
.
├── .devcontainer
│   ├── Dockerfile         # Dockerfile：GPU対応 + LLMライブラリなどをインストール
│   ├── devcontainer.json  # VSCode Dev Container用設定 (任意)
│   └── setup.sh           # postCreateCommand で呼び出すスクリプト (任意)
├── src/                   # (任意) ソースコード配置場所
├── notebooks/             # (任意) Notebook配置場所
└── README.md              # このファイル
```

- `.devcontainer/` は VSCode Dev Container 利用時の構成例。  
- `Dockerfile` の場所や構成はプロジェクトによって異なります。  
- Notebook・コードなどは `src/` や `notebooks/` 以下にお好みで配置してください。

---

## トラブルシューティング

1. **ビルドでエラーが出る / 時間がかかる**  
   - ネットワークが不安定、またはディスク容量不足が多い原因  
   - Virtual disk limit（Docker Desktop）を拡大、あるいは安定したネットワーク環境で再ビルド  
2. **“Operation too slow...” エラー**  
   - ネットワーク速度不足。何度かやり直すか、時間帯を変えて再トライ  
3. **“E: You don't have enough free space”**  
   - Docker に割り当てる容量不足。Docker Desktop の「Resources > Disk Image Size」から拡大  
4. **GPU が見つからない**  
   - `docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi` で確認  
   - NVIDIA Container Toolkit / ドライバが正しくセットアップされているか確認  
5. **特定ライブラリのバージョン依存エラー**  
   - flash-attention や PyTorch+CUDA のバージョンミスマッチ  
   - Dockerfile を修正して依存ライブラリのバージョンを合わせるか、pip install し直す  
