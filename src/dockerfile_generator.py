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
        "ada": "8.9",  # RTX 40xx
        "volta": "7.0",
        "turing": "7.5",
        "pascal": "6.0;6.1",
        "default": "7.0;7.5;8.0;8.6;9.0"
    }
    return arch_map.get(gpu_architecture, arch_map["default"])

def determine_uv_install_method(config: Dict[str, Any]) -> str:
    """uvインストール方法を決定する"""
    if "uv" in config and "install_method" in config["uv"]:
        method = config["uv"]["install_method"]
        
        # 有効な方法のマッピング
        method_map = {
            "standalone": "standalone",
            "pipx": "pip",
            "pip": "direct_pip",
            "direct_pip": "direct_pip"
        }
        
        return method_map.get(method, "standalone")
    
    # デフォルトはスタンドアロン
    return "standalone"

def normalize_library_entry(lib: Dict[str, Any]) -> Dict[str, Any]:
    """ライブラリエントリーを正規化する"""
    normalized = {}
    
    # 名前は必須
    if "name" not in lib:
        raise ValueError("ライブラリエントリーに'name'フィールドが必要です")
    
    normalized["name"] = lib["name"]
    
    # バージョン指定の処理
    if "version" in lib and lib["version"]:
        # 空文字列でない場合のみバージョンを設定
        normalized["version"] = lib["version"]
    elif "install" in lib and lib["install"]:
        # installフラグがTrueの場合はバージョン指定なし
        normalized["install"] = True
    else:
        # デフォルトはインストールする
        normalized["install"] = True
    
    # 追加オプションの処理
    if "extra" in lib:
        normalized["extra"] = lib["extra"]
    
    if "source" in lib:
        normalized["source"] = lib["source"]
    
    return normalized

def prepare_libraries(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """ライブラリプリセットまたはカスタムライブラリを準備する"""
    if config["libraries"]["use_preset"]:
        preset_name = config["libraries"]["preset"]
        raw_libraries = get_libraries_from_preset(preset_name)
    else:
        # カスタムライブラリを全てフラットなリストに結合
        raw_libraries = []
        if "custom" in config["libraries"]:
            for category in config["libraries"]["custom"]:
                if isinstance(config["libraries"]["custom"][category], list):
                    raw_libraries.extend(config["libraries"]["custom"][category])
    
    # 各ライブラリエントリーを正規化
    normalized_libraries = []
    for lib in raw_libraries:
        try:
            normalized = normalize_library_entry(lib)
            normalized_libraries.append(normalized)
        except Exception as e:
            print(f"警告: ライブラリエントリーの処理でエラー: {lib} - {str(e)}")
            continue
    
    return normalized_libraries

def prepare_environment_vars(config: Dict[str, Any]) -> List[Dict[str, str]]:
    """環境変数を準備する"""
    env_vars = []
    
    # プリセット環境変数
    if config.get("environment", {}).get("preset", {}).get("hopper", False):
        env_vars.extend([
            {"name": "PYTORCH_CUDA_ALLOC_CONF", "value": "max_split_size_mb:512"},
            {"name": "NCCL_DEBUG", "value": "INFO"},
            {"name": "NCCL_P2P_LEVEL", "value": "NVL"}
        ])
    
    if (config.get("environment", {}).get("preset", {}).get("multi_gpu", False) and 
        config["gpu"]["count"] > 1):
        env_vars.extend([
            {"name": "NCCL_IB_DISABLE", "value": "0"},
            {"name": "NCCL_SOCKET_IFNAME", "value": "^lo,docker"},
            {"name": "NCCL_DEBUG", "value": "INFO"}
        ])
    
    # カスタム環境変数
    if "environment" in config and "custom" in config["environment"]:
        env_vars.extend(config["environment"]["custom"])
    
    return env_vars

def get_template_path() -> str:
    """テンプレートファイルのパスを取得する"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "templates", "dockerfile.j2")

def validate_config_for_generation(config: Dict[str, Any]) -> None:
    """Dockerfile生成前の設定検証（uv対応版）"""
    required_sections = ["base", "gpu", "deep_learning", "libraries"]
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"必須セクション '{section}' が設定にありません")
    
    # 基本設定の検証
    if "cuda_version" not in config["base"]:
        raise ValueError("基本設定に'cuda_version'が必要です")
    
    if "python_version" not in config["base"]:
        raise ValueError("基本設定に'python_version'が必要です")
    
    # GPU設定の検証
    if "architecture" not in config["gpu"]:
        config["gpu"]["architecture"] = "default"  # デフォルト値を設定
    
    if "count" not in config["gpu"]:
        config["gpu"]["count"] = 1  # デフォルト値を設定
    
    # uv設定のデフォルト値設定
    if "uv" not in config:
        config["uv"] = {
            "install_method": "standalone",
            "version": "latest"
        }

def generate_dockerfile(config: Dict[str, Any]) -> str:
    """Dockerfileを生成する（uv対応版）"""
    
    # 設定の事前検証
    validate_config_for_generation(config)
    
    # ライブラリとプリセットの準備
    try:
        libraries = prepare_libraries(config)
    except Exception as e:
        print(f"エラー: ライブラリの準備中に問題が発生しました: {str(e)}")
        libraries = []  # 空のリストで続行
    
    env_vars = prepare_environment_vars(config)
    
    # uv設定の決定
    uv_install_method = determine_uv_install_method(config)
    
    # 追加の設定を結合
    render_config = config.copy()
    render_config["libraries_flat"] = libraries
    render_config["env_vars"] = env_vars
    render_config["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    render_config["uv_install_method"] = uv_install_method
    
    # バージョン短縮形の追加
    cuda_version = config["base"]["cuda_version"]
    cuda_short = cuda_version.replace(".", "")
    render_config["cuda_short"] = cuda_short
    
    # GPUアーキテクチャリストの追加
    render_config["gpu_arch_list"] = get_gpu_arch_list(config["gpu"]["architecture"])
    
    # デフォルト値の設定
    if "workspace" not in render_config:
        render_config["workspace"] = {"directory": "/mnt"}
    
    if "claude_code" not in render_config:
        render_config["claude_code"] = {"install": False}
    
    # テンプレートファイルからDockerfile生成
    try:
        template_path = get_template_path()
        template_dir = os.path.dirname(template_path)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"テンプレートファイルが見つかりません: {template_path}")
        
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(os.path.basename(template_path))
        
        dockerfile_content = template.render(**render_config)
        
        # 生成されたDockerfileの検証
        if "uv --version" not in dockerfile_content:
            print("警告: 生成されたDockerfileにuvバージョン確認が含まれていません")
        
        return dockerfile_content
        
    except Exception as e:
        print(f"エラー: Dockerfileの生成中に問題が発生しました: {str(e)}")
        print(f"設定内容: {render_config}")
        raise

def debug_uv_config(config: Dict[str, Any]) -> None:
    """uv設定のデバッグ情報を出力"""
    print("🔍 uv設定のデバッグ:")
    
    uv_config = config.get("uv", {})
    install_method = determine_uv_install_method(config)
    
    print(f"設定されたインストール方法: {uv_config.get('install_method', 'undefined')}")
    print(f"決定されたインストール方法: {install_method}")
    print(f"uvバージョン: {uv_config.get('version', 'undefined')}")
    
    method_descriptions = {
        "standalone": "スタンドアロンインストーラー（推奨・最速）",
        "pip": "pipx経由（最も確実）",
        "direct_pip": "pip直接インストール（最もシンプル）"
    }
    
    print(f"説明: {method_descriptions.get(install_method, '不明')}")
    print("─" * 50)

def debug_libraries_structure(config: Dict[str, Any]) -> None:
    """ライブラリ構造のデバッグ情報を出力"""
    print("🔍 ライブラリ構造のデバッグ:")
    print(f"use_preset: {config['libraries'].get('use_preset', 'undefined')}")
    
    if config["libraries"].get("use_preset", False):
        preset_name = config["libraries"].get("preset", "undefined")
        print(f"プリセット名: {preset_name}")
        
        try:
            libraries = get_libraries_from_preset(preset_name)
            print(f"プリセットライブラリ数: {len(libraries)}")
            for i, lib in enumerate(libraries[:3]):  # 最初の3つを表示
                print(f"  [{i}]: {lib}")
        except Exception as e:
            print(f"プリセット読み込みエラー: {str(e)}")
    
    elif "custom" in config["libraries"]:
        print("カスタムライブラリ:")
        for category, libs in config["libraries"]["custom"].items():
            print(f"  {category}: {len(libs)} items")
            for i, lib in enumerate(libs[:2]):  # 最初の2つを表示
                print(f"    [{i}]: {lib}")
    
    # 正規化後のライブラリ
    try:
        normalized = prepare_libraries(config)
        print(f"正規化後ライブラリ数: {len(normalized)}")
        for i, lib in enumerate(normalized[:3]):  # 最初の3つを表示
            print(f"  正規化[{i}]: {lib}")
    except Exception as e:
        print(f"正規化エラー: {str(e)}")
    
    print("─" * 50)