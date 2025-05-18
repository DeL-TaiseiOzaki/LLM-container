#!/usr/bin/env python3
"""
ビルドヘルパースクリプト - コンテナビルド関連のユーティリティ関数
"""
import os
import platform
import subprocess
from typing import Dict, Any, Tuple, Optional


def check_docker_installed() -> bool:
    """Dockerがインストールされているか確認"""
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def check_nvidia_docker() -> bool:
    """NVIDIA Docker (Container Toolkit) が利用可能か確認"""
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "--gpus", "all", "nvidia/cuda:11.0.3-base-ubuntu20.04", "nvidia-smi"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except subprocess.SubprocessError:
        return False

def detect_system_gpu() -> Dict[str, Any]:
    """システムのGPU情報を検出"""
    gpu_info = {
        "detected": False,
        "count": 0,
        "names": [],
        "cuda_version": None,
        "architecture": None
    }
    
    # Linux環境での検出
    if platform.system() == "Linux":
        try:
            # nvidia-smiでGPU情報を取得
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,count,driver_version", "--format=csv,noheader"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                gpu_info["detected"] = True
                gpu_info["count"] = len(lines)
                
                for line in lines:
                    parts = line.split(", ")
                    if len(parts) >= 3:
                        gpu_name = parts[0]
                        gpu_info["names"].append(gpu_name)
                        
                        # アーキテクチャの推定
                        if "A100" in gpu_name or "H100" in gpu_name:
                            gpu_info["architecture"] = "hopper" if "H100" in gpu_name else "ampere"
                        elif "V100" in gpu_name:
                            gpu_info["architecture"] = "volta"
                        elif "T4" in gpu_name:
                            gpu_info["architecture"] = "turing"
                        elif "RTX" in gpu_name or "GTX" in gpu_name:
                            if "3090" in gpu_name or "4090" in gpu_name:
                                gpu_info["architecture"] = "ampere"
                            
                # CUDAバージョンの検出
                cuda_result = subprocess.run(
                    ["nvcc", "--version"], 
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                if cuda_result.returncode == 0:
                    for line in cuda_result.stdout.split("\n"):
                        if "release" in line:
                            parts = line.split("release ")
                            if len(parts) > 1:
                                cuda_version = parts[1].split(",")[0]
                                gpu_info["cuda_version"] = cuda_version
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    return gpu_info

def suggest_config_from_system() -> Dict[str, Any]:
    """システム情報からの推奨設定を提案"""
    gpu_info = detect_system_gpu()
    
    # デフォルト設定
    suggested_config = {
        "base": {
            "cuda_version": "11.8",  # 幅広く互換性のあるバージョン
            "python_version": "3.10"
        },
        "gpu": {
            "count": gpu_info["count"] if gpu_info["detected"] else 0,
            "architecture": gpu_info["architecture"] if gpu_info["architecture"] else "default"
        },
        "deep_learning": {
            "pytorch": {
                "version": "2.0.0"  # 安定したバージョン
            },
            "attention": {
                "flash_attention": True,
                "flash_attention_version": "2.0.0"
            }
        }
    }
    
    # 検出されたCUDAバージョンに基づいて設定を調整
    if gpu_info["cuda_version"]:
        cuda_ver = gpu_info["cuda_version"]
        major_minor = ".".join(cuda_ver.split(".")[:2])
        suggested_config["base"]["cuda_version"] = major_minor
        
        # CUDAバージョンに適したPyTorch/FlashAttentionバージョンを設定
        if major_minor >= "12.0":
            suggested_config["deep_learning"]["pytorch"]["version"] = "2.1.0"
            suggested_config["deep_learning"]["attention"]["flash_attention_version"] = "2.3.0"
        
    return suggested_config

def get_container_resources(container_name: str) -> Optional[Dict[str, Any]]:
    """実行中のコンテナのリソース使用状況を取得"""
    try:
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}", container_name],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:  # ヘッダー行を含む
                parts = lines[1].split("\t")
                if len(parts) >= 7:
                    return {
                        "name": parts[0],
                        "cpu_percent": parts[1],
                        "mem_usage": parts[2],
                        "mem_percent": parts[3],
                        "net_io": parts[4],
                        "block_io": parts[5],
                        "pids": parts[6]
                    }
    except subprocess.SubprocessError:
        pass
    
    return None