# LLM Docker Environment

本リポジトリでは、**LLM（Large Language Model）の開発・推論・ファインチューニング**、および**エージェントシステム構築**に適した Docker イメージを作成・共有しています。  

- **GPU 対応**（NVIDIA Container Toolkit 必須）  
- **Jupyter Lab** だけでなく、**任意のアプリケーションやフレームワーク**（FastAPI, Flask, CLI ツール等）で利用可能  
- 主なライブラリ:
  - Python + Mambaforge (Miniforge)
  - PyTorch + CUDA
  - Transformers, Accelerate, Datasets, Sentencepiece
  - flash-attention, vllm, deepspeed, xformers など
  - ベクトル検索 (Faiss)
  - エージェントや RAG に便利な langchain, llama_index
  - データサイエンス向け (polars, pyarrow, scikit-image) など

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

- **Python 3.11 + Mambaforge**  
  - 柔軟に Python パッケージを管理し、依存関係を簡潔に保持  
- **PyTorch + CUDA 12.4**  
  - GPU を活用した高速な推論・学習（NVIDIA GPU）  
- **主要ライブラリ**  
  - **LLM 関連**: transformers, accelerate, peft, bitsandbytes, sentencepiece  
  - **学習最適化**: flash-attention, deepspeed, xformers  
  - **推論高速化**: vllm, optimum\[onnxruntime-gpu\]  
  - **RAG/エージェント**: langchain, llama_index  
  - **データ解析**: numpy, pandas, polars, pyarrow, scipy, scikit-learn, scikit-image  
  - **ベクトル検索**: faiss-gpu  
  - **可視化 / Notebook**: matplotlib, jupyterlab, ipywidgets  
  - **実験管理**: wandb, ray\[default\]  
  - **補助ツール**: openai, anthropic, huggingface_hub, evaluate  
- **開発効率化ツール**  
  - black, flake8, isort, mypy, pre-commit, tqdm など

---

## 事前準備

1. **Docker** がインストールされていること  
   - [Docker Desktop](https://www.docker.com/products/docker-desktop) または [Docker Engine](https://docs.docker.com/engine/install/)  
   - `docker version` で動作確認
2. **NVIDIA Container Toolkit** がインストールされていること (GPU 利用する場合)  
   - [公式ドキュメント](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) を参考にセットアップ  
   - セットアップ後、下記コマンドが正常に実行できれば OK  
     ```bash
     docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
     ```

---

## ビルド方法

1. **リポジトリをクローン**

```bash
git clone <このリポジトリのURL>
cd <クローンしたディレクトリ>
```

2. **Docker イメージをビルド**

```bash
docker build -t my-llm-image:latest -f .devcontainer/Dockerfile .
```

- `my-llm-image:latest` はイメージに付けるタグ名（任意）  
- `Dockerfile` はビルド用 Dockerfile のパス。変更している場合は適宜修正  

ビルド途中、通信速度・ストレージ不足等で失敗する可能性があります。何度かリトライするか、通信環境やディスク容量を見直してください。

---

## 利用方法

### 4.1　コンテナの起動

GPU を使う例:  
```bash
docker run --gpus all --rm -it -v $HOME:/mnt -p 8888:8888 \
  --name my-llm-container \
  my-llm-image:latest \
  /bin/bash
```

コンテナ内に入ったら、Jupyter Lab を起動して Notebook 開発を進められます:
```bash
jupyter lab --ip 0.0.0.0 --allow-root --no-browser
```
すると、ホストマシンのブラウザで [http://localhost:8888](http://localhost:8888) にアクセスし、表示されるトークンを使って Jupyter Lab に入れます。

### 4.2 CLI / FastAPI / その他アプリケーション

Notebook 以外にも、コンテナ内で自由にコマンドを実行できます。
```bash
# 例: Python スクリプトを実行
python scripts/my_llm_script.py

# 例: FastAPI アプリを起動
uvicorn my_app:app --host 0.0.0.0 --port 8080
```
ポート番号を変更した場合は、コンテナ起動時の `-p` オプションを合わせて修正してください。

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
   - `docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi` で確認  
   - NVIDIA Container Toolkit / ドライバが正しくセットアップされているか確認  
5. **特定ライブラリのバージョン依存エラー**  
   - flash-attention, PyTorch+CUDA, xformers のバージョンミスマッチ  
   - Dockerfile を修正して依存ライブラリのバージョンを合わせるか、pip/conda でアップデート or ダウングレード  

---
