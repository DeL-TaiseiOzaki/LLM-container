#!/usr/bin/env python3
"""
Simple LLM Docker Builder
シンプルで実用的なLLM開発環境構築ツール
"""

import os
import sys
import yaml
import argparse
import subprocess
from datetime import datetime
from jinja2 import Template

# CUDA-PyTorch対応表（PyTorch公式サイトより 2025.1月更新）
CUDA_PYTORCH = {
    "11.8": {
        "pytorch_versions": ["2.7.0", "2.6.0", "2.5.1", "2.4.1", "2.3.1"],
        "default": "2.5.1",  # 安定版を推奨
        "index_url": "https://download.pytorch.org/whl/cu118"
    },
    "12.1": {
        "pytorch_versions": ["2.5.1", "2.4.1", "2.3.1"],
        "default": "2.5.1",
        "index_url": "https://download.pytorch.org/whl/cu121"
    },
    "12.4": {
        "pytorch_versions": ["2.6.0", "2.5.1", "2.4.1"],
        "default": "2.6.0",
        "index_url": "https://download.pytorch.org/whl/cu124"
    },
    "12.6": {
        "pytorch_versions": ["2.7.0", "2.6.0"],
        "default": "2.7.0",  # 最新版
        "index_url": "https://download.pytorch.org/whl/cu126"
    },
    "12.8": {
        "pytorch_versions": ["2.7.0"],
        "default": "2.7.0",  # H100用最新
        "index_url": "https://download.pytorch.org/whl/cu128"
    }
}

def load_config(config_path):
    """設定ファイルを読み込む"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def validate_config(config):
    """設定を検証"""
    errors = []
    
    # CUDA バージョンチェック
    if config['cuda_version'] not in CUDA_PYTORCH:
        errors.append(f"サポートされていないCUDAバージョン: {config['cuda_version']}")
        errors.append(f"利用可能: {', '.join(sorted(CUDA_PYTORCH.keys()))}")
    
    # PyTorchバージョンチェック（オプション）
    if 'pytorch_version' in config:
        cuda_info = CUDA_PYTORCH.get(config['cuda_version'], {})
        if config['pytorch_version'] not in cuda_info.get('pytorch_versions', []):
            errors.append(f"CUDA {config['cuda_version']}では PyTorch {config['pytorch_version']} は利用できません")
            errors.append(f"利用可能: {', '.join(cuda_info.get('pytorch_versions', []))}")
    
    # Python バージョンチェック
    valid_python = ["3.9", "3.10", "3.11", "3.12"]
    if config['python_version'] not in valid_python:
        errors.append(f"サポートされていないPythonバージョン: {config['python_version']}")
        errors.append(f"利用可能: {', '.join(valid_python)}")
    
    if errors:
        print("❌ 設定エラー:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("✅ 設定検証OK")

def generate_dockerfile(config):
    """Dockerfileを生成"""
    
    # PyTorchバージョンとURLを取得
    cuda_info = CUDA_PYTORCH[config['cuda_version']]
    
    # ユーザー指定のPyTorchバージョンを優先、なければデフォルトを使用
    pytorch_version = config.get('pytorch_version', cuda_info['default'])
    
    # 互換性確認
    if pytorch_version not in cuda_info['pytorch_versions']:
        print(f"⚠️ 警告: PyTorch {pytorch_version} は CUDA {config['cuda_version']} で未検証です")
        pytorch_version = cuda_info['default']
        print(f"  → PyTorch {pytorch_version} を使用します")
    
    # テンプレートを読み込む
    template_path = os.path.join('templates', 'Dockerfile.j2')
    with open(template_path, 'r') as f:
        template = Template(f.read())
    
    # 設定を準備
    render_config = {
        'cuda_version': config['cuda_version'],
        'cuda_short': config['cuda_version'].replace('.', ''),
        'python_version': config['python_version'],
        'pytorch_version': pytorch_version,
        'pytorch_index_url': cuda_info['index_url'],
        'transformers_version': config['transformers_version'],
        'packages': config['packages'],
        'claude_code': config.get('claude_code', False),
        'jupyter': config.get('jupyter', False),
        'mount_path': config.get('mount_path', '/workspace'),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Dockerfile生成
    dockerfile_content = template.render(**render_config)
    
    # ファイルに書き込む
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    print(f"✅ Dockerfile生成完了 (PyTorch {pytorch_version} with CUDA {config['cuda_version']})")
    return dockerfile_content

def build_image(config):
    """Dockerイメージをビルド"""
    image_name = f"llm-env:{config['cuda_version']}"
    
    print(f"🔨 イメージをビルド中: {image_name}")
    
    cmd = ["docker", "build", "-t", image_name, "."]
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"✅ ビルド成功: {image_name}")
        return image_name
    else:
        print("❌ ビルドに失敗しました")
        sys.exit(1)

def run_container(config, image_name):
    """コンテナを起動"""
    container_name = config.get('container_name', 'llm-dev')
    mount_path = config.get('mount_path', '/workspace')
    
    # 既存のコンテナを停止
    subprocess.run(["docker", "stop", container_name], capture_output=True)
    subprocess.run(["docker", "rm", container_name], capture_output=True)
    
    # コンテナ起動コマンド
    cmd = [
        "docker", "run",
        "--gpus", "all",
        "--name", container_name,
        "-v", f"{os.path.expanduser('~')}:{mount_path}",
        "--shm-size", "8g",
        "-it",
        "-d",
        image_name,
        "/bin/bash"
    ]
    
    print(f"🚀 コンテナを起動中: {container_name}")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"✅ コンテナ起動成功: {container_name}")
        print(f"\n📝 接続方法:")
        print(f"  docker exec -it {container_name} bash")
        if config.get('jupyter'):
            print(f"\n🌐 Jupyter Lab起動:")
            print(f"  docker exec -it {container_name} jupyter lab --ip 0.0.0.0 --allow-root")
    else:
        print("❌ コンテナ起動に失敗しました")

def list_packages(config):
    """選択されたパッケージを表示"""
    cuda_info = CUDA_PYTORCH[config['cuda_version']]
    pytorch_version = config.get('pytorch_version', cuda_info['default'])
    
    print("\n📦 インストールされるパッケージ:")
    print("  [必須]")
    print(f"    - PyTorch {pytorch_version} (CUDA {config['cuda_version']})")
    print(f"    - Transformers {config['transformers_version']}")
    
    print("  [オプション]")
    for pkg, enabled in config['packages'].items():
        if enabled:
            print(f"    - {pkg}")
    
    if config.get('claude_code'):
        print("    - Claude Code")
    
    if config.get('jupyter'):
        print("    - Jupyter Lab")
    
    print(f"\n💡 CUDA {config['cuda_version']} で利用可能なPyTorch:")
    for ver in cuda_info['pytorch_versions']:
        if ver == pytorch_version:
            print(f"    - {ver} ← 選択中")
        else:
            print(f"    - {ver}")

def main():
    parser = argparse.ArgumentParser(
        description="Simple LLM Docker Builder - シンプルで実用的なLLM環境構築"
    )
    
    parser.add_argument(
        'command',
        choices=['build', 'run', 'all', 'list'],
        help='実行するコマンド'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='設定ファイルのパス (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    # 設定を読み込む
    if not os.path.exists(args.config):
        print(f"❌ 設定ファイルが見つかりません: {args.config}")
        sys.exit(1)
    
    config = load_config(args.config)
    
    # 設定を検証
    validate_config(config)
    
    if args.command == 'list':
        list_packages(config)
    
    elif args.command == 'build':
        generate_dockerfile(config)
        image_name = build_image(config)
    
    elif args.command == 'run':
        image_name = f"llm-env:{config['cuda_version']}"
        run_container(config, image_name)
    
    elif args.command == 'all':
        list_packages(config)
        generate_dockerfile(config)
        image_name = build_image(config)
        run_container(config, image_name)
    
    print("\n✨ 完了!")

if __name__ == "__main__":
    main()