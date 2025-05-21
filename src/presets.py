#!/usr/bin/env python3
from typing import Dict, Any, List

# ライブラリプリセット
LIBRARY_PRESETS = {
    "minimal": [
        {"name": "transformers", "version": ">=4.51.3"},
        {"name": "numpy", "install": True},
        {"name": "pandas", "install": True},
        {"name": "matplotlib", "install": True}
    ],
    "standard": [
        {"name": "transformers", "version": ">=4.51.3"},
        {"name": "accelerate", "version": ">=1.7.0"},
        {"name": "peft", "version": ">=0.15.2"},
        {"name": "datasets", "install": True},
        {"name": "sentencepiece", "install": True},
        {"name": "numpy", "install": True},
        {"name": "pandas", "install": True},
        {"name": "matplotlib", "install": True},
        {"name": "scipy", "install": True},
        {"name": "scikit-learn", "install": True},
        {"name": "jupyterlab", "install": True}
    ],
    "full": [
        # トランスフォーマー系
        {"name": "transformers", "version": ">=4.51.3"},
        {"name": "accelerate", "version": ">=1.7.0"},
        {"name": "peft", "version": ">=0.15.2"},
        {"name": "trl", "version": ">=0.17.0"},
        {"name": "datasets", "install": True},
        {"name": "evaluate", "install": True},
        {"name": "sentencepiece", "install": True},
        {"name": "safetensors", "install": True},
        {"name": "einops", "install": True},
        
        # LLM関連
        {"name": "unsloth", "version": ">=2025.3.14"},
        {"name": "torchtune", "install": True},
        {"name": "langchain", "install": True},
        {"name": "llama-index", "version": ">=0.10.0"},
        {"name": "optimum", "extra": "[onnxruntime-gpu]"},
        {"name": "vllm", "version": ">=0.9.0"},
        {"name": "lightllm", "install": True},
        {"name": "huggingface_hub", "install": True},
        
        # 最適化ツール
        {"name": "deepspeed", "version": ">=0.16.1"},
        {"name": "ray", "extra": "[default]"},
        
        # データ処理
        {"name": "numpy", "install": True},
        {"name": "pandas", "install": True},
        {"name": "pyarrow", "install": True},
        {"name": "polars", "install": True},
        {"name": "faiss-gpu", "install": True},
        
        # ベクトルデータベース
        {"name": "milvus-client", "install": True},
        {"name": "qdrant-client", "install": True},
        {"name": "chromadb", "install": True},
        
        # 可視化・開発ツール
        {"name": "matplotlib", "install": True},
        {"name": "scipy", "install": True},
        {"name": "scikit-learn", "install": True},
        {"name": "scikit-image", "install": True},
        {"name": "wandb", "install": True},
        {"name": "jupyterlab", "install": True},
        {"name": "ipywidgets", "install": True},
        {"name": "tqdm", "install": True},
        
        # APIクライアント
        {"name": "openai", "install": True},
        {"name": "anthropic", "install": True},
        
        # 開発ツール
        {"name": "black", "install": True},
        {"name": "flake8", "install": True},
        {"name": "isort", "install": True},
        {"name": "mypy", "install": True},
        {"name": "pre-commit", "install": True}
    ],
    "research": [
        # Full環境のすべて + 研究特化の追加ライブラリ
        {"name": "transformers", "version": ">=4.51.3"},
        {"name": "accelerate", "version": ">=1.7.0"},
        {"name": "peft", "version": ">=0.15.2"},
        {"name": "trl", "version": ">=0.17.0"},
        {"name": "datasets", "install": True},
        {"name": "evaluate", "install": True},
        
        # 研究特化の追加ライブラリ
        {"name": "torch-geometric", "install": True},
        {"name": "pytorch-lightning", "install": True},
        {"name": "ml-collections", "install": True},
        {"name": "optuna", "install": True},
        {"name": "statsmodels", "install": True},
        {"name": "seaborn", "install": True},
        {"name": "plotly", "install": True},
        {"name": "streamlit", "install": True},
        {"name": "ax-platform", "install": True},
        {"name": "mlflow", "install": True},
        {"name": "axolotl", "install": True}
    ]
}

def get_libraries_from_preset(preset_name: str) -> List[Dict[str, Any]]:
    """プリセット名からライブラリリストを取得する"""
    if preset_name in LIBRARY_PRESETS:
        return LIBRARY_PRESETS[preset_name]
    else:
        print(f"警告: プリセット '{preset_name}' が見つかりません。'standard' を使用します。")
        return LIBRARY_PRESETS["standard"]