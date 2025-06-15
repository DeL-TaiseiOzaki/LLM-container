#!/usr/bin/env python3
import os
import datetime
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
from .presets import get_libraries_from_preset

def get_gpu_arch_list(gpu_architecture: str) -> str:
    """GPUアーキテクチャに基づいてCUDA compute capabilityリストを返す"""
    arch_map = {
        "hopper": "9.0",
        "ampere": "8.0;8.6",
        "volta": "7.0",
        "turing": "7.5",
        "pascal": "6.0;6.1",
        "default": "7.0;7.5;8.0;8.6;9.0"
    }
    return arch_map.get(gpu_architecture, arch_map["default"])

def prepare_libraries(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """ライブラリプリセットまたはカスタムライブラリを準備する"""
    if config["libraries"]["use_preset"]:
        preset_name = config["libraries"]["preset"]
        return get_libraries_from_preset(preset_name)
    else:
        # カスタムライブラリを全てフラットなリストに結合
        libraries = []
        for category in config["libraries"]["custom"]:
            libraries.extend(config["libraries"]["custom"][category])
        return libraries

def prepare_environment_vars(config: Dict[str, Any]) -> List[Dict[str, str]]:
    """環境変数を準備する"""
    env_vars = []
    
    # プリセット環境変数
    if config["environment"]["preset"]["hopper"]:
        env_vars.extend([
            {"name": "PYTORCH_CUDA_ALLOC_CONF", "value": "max_split_size_mb:512"},
            {"name": "NCCL_DEBUG", "value": "INFO"},
            {"name": "NCCL_P2P_LEVEL", "value": "NVL"}
        ])
    
    if config["environment"]["preset"]["multi_gpu"] and config["gpu"]["count"] > 1:
        env_vars.extend([
            {"name": "NCCL_IB_DISABLE", "value": "0"},
            {"name": "NCCL_SOCKET_IFNAME", "value": "^lo,docker"},
            {"name": "NCCL_DEBUG", "value": "INFO"}
        ])
    
    # カスタム環境変数
    if "custom" in config["environment"]:
        env_vars.extend(config["environment"]["custom"])
    
    return env_vars

def get_template_path() -> str:
    """テンプレートファイルのパスを取得する"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "templates", "dockerfile.j2")

def generate_dockerfile(config: Dict[str, Any]) -> str:
    """Dockerfileを生成する"""
    # ライブラリとプリセットの準備
    libraries = prepare_libraries(config)
    env_vars = prepare_environment_vars(config)
    
    # 追加の設定を結合
    render_config = config.copy()
    render_config["libraries_flat"] = libraries
    render_config["env_vars"] = env_vars
    render_config["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # バージョン短縮形の追加
    cuda_short = config["base"]["cuda_version"].replace(".", "")
    render_config["cuda_short"] = cuda_short
    
    # GPUアーキテクチャリストの追加
    render_config["gpu_arch_list"] = get_gpu_arch_list(config["gpu"]["architecture"])
    
    # テンプレートファイルからDockerfile生成
    template_dir = os.path.dirname(get_template_path())
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(os.path.basename(get_template_path()))
    
    return template.render(**render_config)