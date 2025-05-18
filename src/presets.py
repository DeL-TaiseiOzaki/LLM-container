#!/usr/bin/env python3
from typing import Dict, Any, List

# ライブラリプリセット
LIBRARY_PRESETS = {
    "minimal": [
        {"name": "transformers", "version": ">=4.40.0"},
        {"name": "numpy", "install": True},
        {"name": "pandas", "install": True},
        {"name": "matplotlib", "install": True}
    ],
    "standard": [
        {"name": "transformers", "version": ">=4.40.0"},
        {"name": "accelerate", "version": ">=0.29.3"},
        {"name": "peft", "version": ">=0.10.0"},
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
        {"name": "transformers", "version": ">=4.40.0"},
        {"name": "accelerate", "version": ">=0.29.3"},
        {"name": "peft", "version": ">=0.10.0"},
        {"name": "trl", "version": ">=0.8.6"},
        {"name": "datasets", "install": True},
        {"name": "evaluate", "install": True},
        {"name": "sentencepiece", "install": True},
        {"name": "safetensors", "install": True},
        {"name": "einops", "install": True},
        
        # LLM関連
        {"name": "unsloth", "source": "git+https://github.com/unslothai/unsloth.git"},
        {"name": "langchain", "install": True},
        {"name": "llama-index", "version": ">=0.10.0"},
        {"name": "optimum", "extra": "[onnxruntime-gpu]"},
        {"name": "vllm", "install": True},
        {"name": "huggingface_hub", "install": True},
        
        # 最適化ツール
        {"name": "deepspeed", "install": True},
        {"name": "ray", "extra": "[default]"},
        
        # データ処理
        {"name": "numpy", "install": True},
        {"name": "pandas", "install": True},
        {"name": "pyarrow", "install": True},
        {"name": "polars", "install": True},
        {"name": "faiss-gpu", "install": True},
        
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
        {"name": "transformers", "version": ">=4.40.0"},
        {"name": "accelerate", "version": ">=0.29.3"},
        {"name": "peft", "version": ">=0.10.0"},
        {"name": "trl", "version": ">=0.8.6"},
        # ...（fullの内容）
        
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
        {"name": "mlflow", "install": True}
    ]
}

def get_libraries_from_preset(preset_name: str) -> List[Dict[str, Any]]:
    """プリセット名からライブラリリストを取得する"""
    if preset_name in LIBRARY_PRESETS:
        return LIBRARY_PRESETS[preset_name]
    else:
        print(f"警告: プリセット '{preset_name}' が見つかりません。'standard' を使用します。")
        return LIBRARY_PRESETS["standard"]