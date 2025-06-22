#!/usr/bin/env python3
import os
import sys
import argparse
import shutil
from typing import List, Optional

from src.config_loader import load_config, load_default_config, load_compatibility_maps, merge_configs
from src.compatibility import validate_config
from src.dockerfile_generator import generate_dockerfile
from src.dependency_resolver import DependencyResolver, auto_resolve_config, print_resolution_report

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
        "purple": "\033[0;35m",
        "cyan": "\033[0;36m",
        "reset": "\033[0m"
    }
    
    print(f"{colors.get(color, colors['reset'])}{text}{colors['reset']}")

def initialize_project():
    """プロジェクトの初期化"""
    print_colored("プロジェクトを初期化しています...", "blue")
    
    # ディレクトリ構造の作成
    setup_directories()
    
    print_colored("プロジェクトの初期化が完了しました。", "green")

def validate_and_warn(config, compatibility_maps) -> List[str]:
    """設定を検証し、警告を表示する"""
    is_valid, warnings = validate_config(config, compatibility_maps)
    
    if not is_valid:
        print_colored("設定に問題があります:", "yellow")
        for warning in warnings:
            print_colored(f"  - {warning}", "yellow")
    
    return warnings

def resolve_dependencies_interactive(config, compatibility_maps, strategy: str = "stability"):
    """依存関係を解決し、結果を表示"""
    print_colored("🔧 依存関係を自動解決しています...", "cyan")
    
    resolver = DependencyResolver(compatibility_maps)
    resolution = resolver.resolve_dependencies(config, strategy)
    
    # 解決結果の表示
    print_resolution_report(resolution)
    
    if resolution.success:
        # 解決されたバージョンで設定を更新
        resolved_config = auto_resolve_config(config, compatibility_maps)
        
        print_colored("\n📝 設定が自動更新されました", "green")
        return resolved_config, resolution
    else:
        print_colored("\n❌ 依存関係の解決に失敗しました", "red")
        return config, resolution

def suggest_config_optimization(config, compatibility_maps):
    """設定の最適化提案"""
    print_colored("💡 設定最適化の提案", "purple")
    
    resolver = DependencyResolver(compatibility_maps)
    
    # 異なる戦略での解決を試行
    strategies = ["stability", "performance", "compatibility"]
    results = {}
    
    for strategy in strategies:
        resolution = resolver.resolve_dependencies(config, strategy)
        if resolution.success:
            results[strategy] = resolution
    
    if not results:
        print_colored("最適化提案はありません。", "yellow")
        return config
    
    print("\n利用可能な戦略:")
    for strategy, resolution in results.items():
        print(f"\n🎯 {strategy.upper()}戦略:")
        key_packages = {k: v for k, v in resolution.packages.items() 
                       if k in ["torch", "transformers", "flash_attn"]}
        for pkg, version in key_packages.items():
            print(f"  {pkg}: {version}")
    
    # デフォルトは安定性戦略
    return results.get("stability", results[list(results.keys())[0]])

def auto_complete_config(partial_config_path: str, output_path: str = None):
    """部分設定から完全設定を生成"""
    print_colored("🛠️  設定の自動補完を開始します...", "blue")
    
    # 部分設定の読み込み
    partial_config = load_config(partial_config_path)
    compatibility_maps = load_compatibility_maps()
    
    try:
        # 自動補完
        complete_config = auto_resolve_config(partial_config, compatibility_maps)
        
        # 出力ファイル名の決定
        if output_path is None:
            base_name = os.path.splitext(partial_config_path)[0]
            output_path = f"{base_name}_complete.yaml"
        
        # 補完された設定を保存
        import yaml
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(complete_config, f, default_flow_style=False, allow_unicode=True)
        
        print_colored(f"✅ 完全設定が生成されました: {output_path}", "green")
        
        # 依存関係解決の表示
        resolver = DependencyResolver(compatibility_maps)
        resolution = resolver.resolve_dependencies(complete_config)
        print_resolution_report(resolution)
        
    except Exception as e:
        print_colored(f"❌ 自動補完に失敗しました: {str(e)}", "red")

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

def run_docker_container(image_name: str, container_name: str, gpu_count: int, shm_size: str = "4g") -> bool:
    """Dockerコンテナを起動する"""
    print_colored(f"コンテナを起動しています: {container_name}", "blue")
    
    # GPUオプションを設定
    gpu_option = "--gpus all" if gpu_count > 0 else ""
    
    # 共有メモリサイズを追加
    import subprocess
    result = subprocess.run(
        f"docker run {gpu_option} --shm-size={shm_size} --rm -itd -v ~/:/mnt --name {container_name} {image_name} /bin/bash",
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
    parser = argparse.ArgumentParser(description="LLM Docker環境ビルドツール（依存関係ソルバー統合版）")
    
    # サブコマンドの設定
    subparsers = parser.add_subparsers(dest="command", help="コマンド")
    
    # 初期化コマンド
    init_parser = subparsers.add_parser("init", help="プロジェクトを初期化")
    
    # 自動補完コマンド（新規）
    complete_parser = subparsers.add_parser("complete", help="部分設定から完全設定を自動生成")
    complete_parser.add_argument("--input", required=True, help="部分設定ファイルのパス")
    complete_parser.add_argument("--output", help="出力ファイルのパス（省略時は自動生成）")
    
    # 解決コマンド（新規）
    resolve_parser = subparsers.add_parser("resolve", help="依存関係を解決")
    resolve_parser.add_argument("--config", default="config.yaml", help="設定ファイルのパス")
    resolve_parser.add_argument("--strategy", choices=["stability", "performance", "compatibility"], 
                               default="stability", help="解決戦略")
    resolve_parser.add_argument("--optimize", action="store_true", help="最適化提案を表示")
    
    # 検証コマンド（強化）
    validate_parser = subparsers.add_parser("validate", help="設定を検証")
    validate_parser.add_argument("--config", default="config.yaml", help="設定ファイルのパス")
    validate_parser.add_argument("--auto-fix", action="store_true", help="自動修正を試行")
    
    # 生成コマンド
    generate_parser = subparsers.add_parser("generate", help="Dockerfileを生成")
    generate_parser.add_argument("--config", default="config.yaml", help="設定ファイルのパス")
    generate_parser.add_argument("--output", default="Dockerfile", help="出力ファイルのパス")
    generate_parser.add_argument("--auto-resolve", action="store_true", help="依存関係を自動解決")
    
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
    
    # オールインワンコマンド（強化）
    all_parser = subparsers.add_parser("all", help="解決、生成、ビルド、実行を一度に行う")
    all_parser.add_argument("--config", default="config.yaml", help="設定ファイルのパス")
    all_parser.add_argument("--image", default="llm-env:latest", help="イメージ名")
    all_parser.add_argument("--container", default="llm-container", help="コンテナ名")
    all_parser.add_argument("--strategy", choices=["stability", "performance", "compatibility"], 
                          default="stability", help="依存関係解決戦略")
    
    args = parser.parse_args()
    
    # コマンドが指定されていない場合はヘルプを表示
    if not args.command:
        parser.print_help()
        return
    
    # 初期化コマンド
    if args.command == "init":
        initialize_project()
        return
    
    # 自動補完コマンド
    if args.command == "complete":
        auto_complete_config(args.input, args.output)
        return
    
    # 設定を読み込む（初期化と自動補完以外）
    if args.command in ["resolve", "validate", "generate", "build", "all", "run"]:
        if not os.path.exists(args.config):
            print_colored(f"エラー: 設定ファイル {args.config} が見つかりません", "red")
            return
        
        user_config = load_config(args.config)
        default_config = load_default_config()
        config = merge_configs(user_config, default_config)
        compatibility_maps = load_compatibility_maps()
    
    # 解決コマンド
    if args.command == "resolve":
        if args.optimize:
            suggest_config_optimization(config, compatibility_maps)
        else:
            resolved_config, resolution = resolve_dependencies_interactive(
                config, compatibility_maps, args.strategy
            )
        return
    
    # 検証コマンド（強化）
    if args.command == "validate":
        warnings = validate_and_warn(config, compatibility_maps)
        
        if args.auto_fix and warnings:
            print_colored("\n🔧 自動修正を試行します...", "cyan")
            try:
                resolved_config = auto_resolve_config(config, compatibility_maps)
                print_colored("✅ 自動修正が完了しました", "green")
                
                # 修正された設定を保存
                fixed_config_path = args.config.replace('.yaml', '_fixed.yaml')
                import yaml
                with open(fixed_config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(resolved_config, f, default_flow_style=False, allow_unicode=True)
                print_colored(f"修正された設定: {fixed_config_path}", "blue")
            except Exception as e:
                print_colored(f"❌ 自動修正に失敗しました: {str(e)}", "red")
        elif not warnings:
            print_colored("設定に問題はありません", "green")
        return
    
    # 生成コマンド（強化）
    if args.command == "generate":
        # 依存関係の自動解決（オプション）
        if args.auto_resolve:
            print_colored("🔧 依存関係を自動解決してからDockerfileを生成します...", "cyan")
            try:
                config = auto_resolve_config(config, compatibility_maps)
                print_colored("✅ 依存関係が解決されました", "green")
            except Exception as e:
                print_colored(f"⚠️  依存関係解決に失敗。元の設定でDockerfileを生成します: {str(e)}", "yellow")
        
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
            pass
        run_docker_container(args.image, args.name, gpu_count, "4g")
        return
    
    # オールインワンコマンド（強化）
    if args.command == "all":
        print_colored("🚀 全工程（解決→生成→ビルド→実行）を開始します", "purple")
        
        # Step 1: 依存関係解決
        print_colored("\n📋 Step 1: 依存関係解決", "cyan")
        try:
            resolved_config, resolution = resolve_dependencies_interactive(
                config, compatibility_maps, args.strategy
            )
            if not resolution.success:
                print_colored("❌ 依存関係解決に失敗したため、処理を中断します", "red")
                return
            config = resolved_config
        except Exception as e:
            print_colored(f"⚠️  依存関係解決に失敗。元の設定で続行します: {str(e)}", "yellow")
        
        # Step 2: Dockerfile生成
        print_colored("\n📋 Step 2: Dockerfile生成", "cyan")
        dockerfile_content = generate_dockerfile(config)
        dockerfile_path = "Dockerfile"
        
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
        
        print_colored(f"Dockerfileが生成されました: {dockerfile_path}", "green")
        
        # Step 3: イメージビルド
        print_colored("\n📋 Step 3: イメージビルド", "cyan")
        if not build_docker_image(dockerfile_path, args.image):
            return
        
        # Step 4: コンテナ起動
        print_colored("\n📋 Step 4: コンテナ起動", "cyan")
        run_docker_container(args.image, args.container, config["gpu"]["count"], "8g")
        
        print_colored("\n🎉 全工程が完了しました！", "green")
        return

if __name__ == "__main__":
    main()