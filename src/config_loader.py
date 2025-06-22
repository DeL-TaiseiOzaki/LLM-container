#!/usr/bin/env python3
import os
import yaml
from typing import Dict, Any

def load_yaml(file_path: str) -> Dict[str, Any]:
    """YAMLファイルを読み込む"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_config(config_path: str) -> Dict[str, Any]:
    """ユーザー設定を読み込む"""
    return load_yaml(config_path)

def load_default_config() -> Dict[str, Any]:
    """デフォルト設定を読み込む"""
    default_config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        "config", 
        "default_config.yaml"
    )
    return load_yaml(default_config_path)

def load_compatibility_maps() -> Dict[str, Any]:
    """互換性マップを読み込む（更新版）"""
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config",
        "compatibility"
    )
    
    compatibility = {}
    
    # CUDA-PyTorch互換性（更新版）
    cuda_pytorch_path = os.path.join(base_dir, "cuda_pytorch.yaml")
    if os.path.exists(cuda_pytorch_path):
        compatibility["cuda_pytorch"] = load_yaml(cuda_pytorch_path)
    
    # PyTorch-Python互換性
    pytorch_python_path = os.path.join(base_dir, "pytorch_python.yaml")
    if os.path.exists(pytorch_python_path):
        compatibility["pytorch_python"] = load_yaml(pytorch_python_path)
    
    # Flash Attention互換性（更新版）
    flash_attention_path = os.path.join(base_dir, "flash_attention.yaml")
    if os.path.exists(flash_attention_path):
        compatibility["flash_attention"] = load_yaml(flash_attention_path)
    
    # Transformers生態系互換性（新規）
    transformers_ecosystem_path = os.path.join(base_dir, "transformers_ecosystem.yaml")
    if os.path.exists(transformers_ecosystem_path):
        compatibility["transformers_ecosystem"] = load_yaml(transformers_ecosystem_path)
    
    # 古いファイル形式との互換性（レガシーサポート）
    cuda_transformers_path = os.path.join(base_dir, "cuda_transformers.yaml")
    if os.path.exists(cuda_transformers_path):
        compatibility["cuda_transformers"] = load_yaml(cuda_transformers_path)
    
    trl_compatibility_path = os.path.join(base_dir, "trl_compatibility.yaml")
    if os.path.exists(trl_compatibility_path):
        compatibility["trl_compatibility"] = load_yaml(trl_compatibility_path)
    
    return compatibility

def merge_configs(user_config: Dict[str, Any], default_config: Dict[str, Any]) -> Dict[str, Any]:
    """ユーザー設定とデフォルト設定をマージする"""
    result = default_config.copy()
    
    def merge_dict(target, source):
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                merge_dict(target[key], value)
            else:
                target[key] = value
    
    merge_dict(result, user_config)
    return result

def save_config(config: Dict[str, Any], output_path: str) -> None:
    """設定をYAMLファイルに保存する"""
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(
            config, 
            f, 
            default_flow_style=False, 
            allow_unicode=True,
            sort_keys=False,
            indent=2
        )

def validate_config_structure(config: Dict[str, Any]) -> bool:
    """設定構造の基本的な検証"""
    required_sections = ["base", "gpu", "deep_learning"]
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"必須セクション '{section}' が設定にありません")
    
    # 基本設定の検証
    base_required = ["cuda_version", "python_version"]
    for field in base_required:
        if field not in config["base"]:
            raise ValueError(f"基本設定に必須フィールド '{field}' がありません")
    
    return True