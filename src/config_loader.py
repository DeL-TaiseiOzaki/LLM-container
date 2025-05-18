#!/usr/bin/env python3
import os
import yaml
from typing import Dict, Any

def load_yaml(file_path: str) -> Dict[str, Any]:
    """YAMLファイルを読み込む"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
    
    with open(file_path, 'r') as f:
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
    """互換性マップを読み込む"""
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config",
        "compatibility"
    )
    
    compatibility = {}
    
    # CUDA-PyTorch互換性
    cuda_pytorch_path = os.path.join(base_dir, "cuda_pytorch.yaml")
    compatibility["cuda_pytorch"] = load_yaml(cuda_pytorch_path)
    
    # PyTorch-Python互換性
    pytorch_python_path = os.path.join(base_dir, "pytorch_python.yaml")
    compatibility["pytorch_python"] = load_yaml(pytorch_python_path)
    
    # Flash Attention互換性
    flash_attention_path = os.path.join(base_dir, "flash_attention.yaml")
    compatibility["flash_attention"] = load_yaml(flash_attention_path)
    
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