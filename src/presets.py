#!/usr/bin/env python3
from typing import Dict, Any, List

# ライブラリプリセット（修正版）
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
        {"name": "optimum", "extra": "onnxruntime-gpu"},
        {"name": "vllm", "version": ">=0.9.0"},
        {"name": "lightllm", "install": True},
        {"name": "huggingface_hub", "install": True},
        
        # 最適化ツール
        {"name": "deepspeed", "version": ">=0.16.1"},
        {"name": "ray", "extra": "default"},
        
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
        {"name": "axolotl", "install": True},
        
        # 基本ライブラリ
        {"name": "numpy", "install": True},
        {"name": "pandas", "install": True},
        {"name": "matplotlib", "install": True},
        {"name": "scipy", "install": True},
        {"name": "jupyterlab", "install": True}
    ]
}

def get_libraries_from_preset(preset_name: str) -> List[Dict[str, Any]]:
    """プリセット名からライブラリリストを取得する"""
    if preset_name in LIBRARY_PRESETS:
        return LIBRARY_PRESETS[preset_name]
    else:
        print(f"警告: プリセット '{preset_name}' が見つかりません。'standard' を使用します。")
        return LIBRARY_PRESETS["standard"]

def validate_preset_structure() -> bool:
    """プリセット構造の妥当性をチェック"""
    required_fields = ["name"]
    optional_fields = ["version", "install", "extra", "source"]
    
    for preset_name, libraries in LIBRARY_PRESETS.items():
        print(f"検証中: {preset_name} プリセット")
        
        for i, lib in enumerate(libraries):
            # 必須フィールドのチェック
            for field in required_fields:
                if field not in lib:
                    print(f"エラー: {preset_name}[{i}] に必須フィールド '{field}' がありません: {lib}")
                    return False
            
            # 不正フィールドのチェック
            for field in lib.keys():
                if field not in required_fields + optional_fields:
                    print(f"警告: {preset_name}[{i}] に不明なフィールド '{field}': {lib}")
            
            # バージョンまたはinstallフラグのチェック
            has_version = "version" in lib and lib["version"]
            has_install = "install" in lib and lib["install"]
            
            if not has_version and not has_install:
                print(f"警告: {preset_name}[{i}] にバージョンまたはinstallフラグが指定されていません: {lib}")
    
    print("✅ プリセット構造の検証が完了しました")
    return True

def get_preset_info(preset_name: str) -> Dict[str, Any]:
    """プリセットの詳細情報を取得"""
    if preset_name not in LIBRARY_PRESETS:
        return {"error": f"プリセット '{preset_name}' が見つかりません"}
    
    libraries = LIBRARY_PRESETS[preset_name]
    
    info = {
        "name": preset_name,
        "total_packages": len(libraries),
        "versioned_packages": len([lib for lib in libraries if "version" in lib]),
        "latest_packages": len([lib for lib in libraries if "install" in lib and lib["install"]]),
        "packages_with_extras": len([lib for lib in libraries if "extra" in lib])
    }
    
    # カテゴリ別の分類
    categories = {
        "transformers": ["transformers", "accelerate", "peft", "trl"],
        "data": ["datasets", "pandas", "numpy", "pyarrow"],
        "ml": ["scikit-learn", "pytorch-lightning", "optuna"],
        "visualization": ["matplotlib", "plotly", "seaborn"],
        "development": ["jupyterlab", "black", "flake8"]
    }
    
    info["categories"] = {}
    for category, keywords in categories.items():
        count = sum(1 for lib in libraries if any(keyword in lib["name"] for keyword in keywords))
        info["categories"][category] = count
    
    return info

def list_all_presets() -> None:
    """すべてのプリセットの概要を表示"""
    print("📦 利用可能なライブラリプリセット:")
    print("=" * 50)
    
    for preset_name in LIBRARY_PRESETS.keys():
        info = get_preset_info(preset_name)
        print(f"\n🎯 {preset_name.upper()}:")
        print(f"  📊 総パッケージ数: {info['total_packages']}")
        print(f"  📌 バージョン指定: {info['versioned_packages']}")
        print(f"  🆕 最新版使用: {info['latest_packages']}")
        
        if info['categories']:
            print("  📋 主要カテゴリ:")
            for category, count in info['categories'].items():
                if count > 0:
                    print(f"    - {category}: {count}個")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    # プリセット構造の検証
    validate_preset_structure()
    
    # プリセット一覧の表示
    list_all_presets()