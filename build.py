#!/usr/bin/env python3
import os
import sys
import argparse
import shutil
from typing import List, Optional

from src.config_loader import load_config, load_default_config, load_compatibility_maps, merge_configs
from src.compatibility import validate_config
from src.dockerfile_generator import generate_dockerfile

def setup_directories():
    """必要なディレクトリ構造をセットアップする"""
    directories = [
        "config/compatibility",
        "templates",
        "templates/setup_scripts",
        "src"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def print_colored(text: str, color: str = "reset"):
    """色付きテキストを出力する"""
    colors = {
        "red": "\033[0;31m",
        "green": "\033[0;32m",
        "yellow": "\033[1;33m",
        "blue": "\033[0;34m",
        "reset": "\033[0m"
    }
    
    print(f"{colors.get(color, colors['reset'])}{text}{colors['reset']}")

def initialize_project():
    """プロジェクトの初期化"""
    print_colored("プロジェクトを初期化しています...", "blue")
    
    # ディレクトリ構造の作成
    setup_directories()
    
    # 各ファイルのコピーまたは作成処理
    # (実際のコードでは、テンプレートファイルやデフォルト設定などを作成)
    
    print_colored("プロジェクトの初期化が完了しました。", "green")

def validate_and_warn(config, compatibility_maps) -> List[str]:
    """設定を検証し、警告を表示する"""
    is_valid, warnings = validate_config(config, compatibility_maps)
    
    if not is_valid:
        print_colored("設定に問題があります:", "yellow")
        for warning in warnings:
            print_colored(f"  - {warning}", "yellow")
    
    return warnings

def build_docker_image(dockerfile_path: str, image_name: str) -> bool:
    """Dockerイメージをビルドする"""
    print_colored(f"イメージをビルドしています: {image_name}", "blue")
    
    import subprocess
    result = subprocess.run(["docker", "build", "-t", image_name, "-f", dockerfile_path, "."])
    
    if result.returncode != 0:
        print_colored("イメージのビルドに失敗しました", "red")
        return False
    
    print_colored(f"イメージのビルドが完了しました: {image_name}", "green")
    return True

def run_docker_container(image_name: str, container_name: str, gpu_count: int) -> bool:
    """Dockerコンテナを起動する"""
    print_colored(f"コンテナを起動しています: {container_name}", "blue")
    
    # GPUオプションを設定
    gpu_option = "--gpus all" if gpu_count > 0 else ""
    
    import subprocess
    result = subprocess.run(
        f"docker run {gpu_option} --rm -itd -v ~/:/mnt --name {container_name} -p 8888:8888 {image_name} /bin/bash",
        shell=True
    )
    
    if result.returncode != 0:
        print_colored("コンテナの起動に失敗しました", "red")
        return False
    
    print_colored(f"コンテナが起動しました: {container_name}", "green")
    print_colored(f"コンテナに接続するには: docker exec -it {container_name} bash", "blue")
    print_colored(f"Jupyter Labを起動するには: docker exec -it {container_name} jupyter lab --ip 0.0.0.0 --allow-root --no-browser", "blue")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="LLM Docker環境ビルドツール")
    
    # サブコマンドの設定
    subparsers = parser.add_subparsers(dest="command", help="コマンド")
    
    # 初期化コマンド
    init_parser = subparsers.add_parser("init", help="プロジェクトを初期化")
    
    # 検証コマンド
    validate_parser = subparsers.add_parser("validate", help="設定を検証")
    validate_parser.add_argument("--config", default="config.yaml", help="設定ファイルのパス")
    
    # 生成コマンド
    generate_parser = subparsers.add_parser("generate", help="Dockerfileを生成")
    generate_parser.add_argument("--config", default="config.yaml", help="設定ファイルのパス")
    generate_parser.add_argument("--output", default="Dockerfile", help="出力ファイルのパス")
    
    # ビルドコマンド
    build_parser = subparsers.add_parser("build", help="Dockerイメージをビルド")
    build_parser.add_argument("--config", default="config.yaml", help="設定ファイルのパス")
    build_parser.add_argument("--dockerfile", default="Dockerfile", help="Dockerfileのパス")
    build_parser.add_argument("--name", default="llm-env:latest", help="イメージ名")
    
    # 実行コマンド
    run_parser = subparsers.add_parser("run", help="Dockerコンテナを実行")
    run_parser.add_argument("--image", default="llm-env:latest", help="イメージ名")
    run_parser.add_argument("--name", default="llm-container", help="コンテナ名")
    run_parser.add_argument("--config", default="config.yaml", help="設定ファイルのパス") 
    
    # オールインワンコマンド
    all_parser = subparsers.add_parser("all", help="生成、ビルド、実行を一度に行う")
    all_parser.add_argument("--config", default="config.yaml", help="設定ファイルのパス")
    all_parser.add_argument("--image", default="llm-env:latest", help="イメージ名")
    all_parser.add_argument("--container", default="llm-container", help="コンテナ名")
    
    args = parser.parse_args()
    
    # コマンドが指定されていない場合はヘルプを表示
    if not args.command:
        parser.print_help()
        return
    
    # 初期化コマンド
    if args.command == "init":
        initialize_project()
        return
    
    # 設定を読み込む
    if args.command in ["validate", "generate", "build", "all", "run"]:
        if not os.path.exists(args.config):
            print_colored(f"エラー: 設定ファイル {args.config} が見つかりません", "red")
            return
        
        user_config = load_config(args.config)
        default_config = load_default_config()
        config = merge_configs(user_config, default_config)
        compatibility_maps = load_compatibility_maps()
    
    # 検証コマンド
    if args.command == "validate":
        warnings = validate_and_warn(config, compatibility_maps)
        if not warnings:
            print_colored("設定に問題はありません", "green")
        return
    
    # 生成コマンド
    if args.command == "generate":
        # 検証して警告を表示
        warnings = validate_and_warn(config, compatibility_maps)
        
        # Dockerfileを生成
        dockerfile_content = generate_dockerfile(config)
        
        with open(args.output, "w") as f:
            f.write(dockerfile_content)
        
        print_colored(f"Dockerfileが生成されました: {args.output}", "green")
        return
    
    # ビルドコマンド
    if args.command == "build":
        # Dockerfileが存在するか確認
        if not os.path.exists(args.dockerfile):
            print_colored(f"エラー: Dockerfile {args.dockerfile} が見つかりません", "red")
            return
        
        # イメージをビルド
        build_docker_image(args.dockerfile, args.name)
        return
    
    # 実行コマンド
    if args.command == "run":
        gpu_count = 0
        try:
            gpu_count = config.get("gpu", {}).get("count", 0)
        except NameError:
            pass   # config が無いケースは 0 とする
        run_docker_container(args.image, args.name, gpu_count)
        return
    
    # オールインワンコマンド
    if args.command == "all":
        # 検証して警告を表示
        warnings = validate_and_warn(config, compatibility_maps)
        
        # Dockerfileを生成
        dockerfile_content = generate_dockerfile(config)
        dockerfile_path = "Dockerfile"
        
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
        
        print_colored(f"Dockerfileが生成されました: {dockerfile_path}", "green")
        
        # イメージをビルド
        if not build_docker_image(dockerfile_path, args.image):
            return
        
        # コンテナを起動
        run_docker_container(args.image, args.container, config["gpu"]["count"])
        return

if __name__ == "__main__":
    main()