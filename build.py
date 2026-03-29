# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyyaml>=6.0",
#     "jinja2>=3.1.0",
# ]
# ///

import os
import sys
import yaml
import argparse
import subprocess
from datetime import datetime
from jinja2 import Template

# CUDA-PyTorch対応表（2025年1月最新）
CUDA_PYTORCH = {
    "11.8": {
        "pytorch_versions": ["2.7.0", "2.6.0", "2.5.1", "2.4.1", "2.3.1"],
        "default": "2.5.1",  # 安定版
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
        "default": "2.7.0",
        "index_url": "https://download.pytorch.org/whl/cu126"
    },
    "12.8": {
        "pytorch_versions": ["2.7.0"],
        "default": "2.7.0",
        "index_url": "https://download.pytorch.org/whl/cu128"
    }
}

# パッケージ説明
PACKAGE_INFO = {
    "vllm": "高速推論エンジン（PagedAttention）",
    "trl": "強化学習（RLHF/DPO）",
    "unsloth": "高速ファインチューニング（2x高速）",
    "deepspeed": "分散学習フレームワーク",
    "flash_attention2": "Flash Attention 2（メモリ効率）",
    "openai": "OpenAI API クライアント",
    "litellm": "統一LLM APIインターフェース",
    "langchain": "LLMアプリ開発フレームワーク",
    "wandb": "実験管理・モデル追跡",
    "mlflow": "MLOpsプラットフォーム"
}

def check_docker_compose():
    """docker composeコマンドの利用可能性をチェック"""
    # docker compose (新形式) を試す
    try:
        result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            return ["docker", "compose"]
    except:
        pass
    
    # docker-compose (旧形式) を試す
    try:
        result = subprocess.run(["docker-compose", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            return ["docker-compose"]
    except:
        pass
    
    return None

def get_nvidia_cuda_version():
    """ホストマシンのCUDAバージョンを取得"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'CUDA Version:' in line:
                    version = line.split('CUDA Version:')[1].strip().split()[0]
                    major_minor = '.'.join(version.split('.')[:2])
                    return major_minor
    except:
        pass
    return None

def init_config():
    """初期設定ファイルを生成"""
    host_cuda = get_nvidia_cuda_version()
    
    if host_cuda:
        print(f"✅ ホストのCUDAバージョンを検出: {host_cuda}")
        cuda_version = host_cuda
    else:
        print("⚠️  CUDAバージョンを自動検出できませんでした")
        cuda_version = "12.1"  # デフォルト
    
    config = {
        'cuda_version': cuda_version,
        'python_version': '3.11',
        'transformers_version': '4.56.0',
        'packages': {
            'vllm': True,
            'trl': False,
            'unsloth': False,
            'deepspeed': False,
            'flash_attention2': True,
            'openai': True,
            'litellm': False,
            'langchain': False,
            'wandb': False,
            'mlflow': False
        },
        'claude_code': True,
        'jupyter': True,
        'container_name': 'llm-dev',
        'mount_path': '/workspace'
    }
    
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print("✅ config.yaml を生成しました")
    print("\n📝 次のステップ:")
    print("  1. config.yaml を編集して必要なパッケージを選択")
    print("  2. make build でイメージをビルド")
    print("  3. make run でコンテナを起動")

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
    pytorch_version = config.get('pytorch_version', cuda_info['default'])
    
    # 互換性確認
    if pytorch_version not in cuda_info['pytorch_versions']:
        print(f"⚠️  警告: PyTorch {pytorch_version} は CUDA {config['cuda_version']} で未検証です")
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
    
    print(f"✅ Dockerfile生成完了")
    return dockerfile_content

def build_image(config, name=None):
    """Dockerイメージをビルド"""
    image_name = name or f"llm-env:{config['cuda_version']}"
    
    print(f"🔨 イメージをビルド中: {image_name}")
    print("  （初回は10-20分かかる場合があります）")
    
    cmd = ["docker", "build", "-t", image_name, "."]
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"✅ ビルド成功: {image_name}")
        
        # イメージサイズを表示
        size_cmd = ["docker", "images", image_name, "--format", "{{.Size}}"]
        size_result = subprocess.run(size_cmd, capture_output=True, text=True)
        if size_result.returncode == 0:
            print(f"📦 イメージサイズ: {size_result.stdout.strip()}")
        
        return image_name
    else:
        print("❌ ビルドに失敗しました")
        sys.exit(1)

def run_container(image=None, name=None):
    """コンテナを起動"""
    config = load_config('config.yaml')
    container_name = name or config.get('container_name', 'llm-dev')
    image_name = image or f"llm-env:{config['cuda_version']}"
    
    # Docker Composeが利用可能かチェック
    if os.path.exists('docker-compose.yml'):
        compose_cmd = check_docker_compose()
        
        if compose_cmd:
            print(f"🚀 Docker Composeでコンテナを起動中...")
            
            # カスタムコンテナ名が指定された場合は環境変数で渡す
            env = os.environ.copy()
            env['CONTAINER_NAME'] = container_name
            env['IMAGE_NAME'] = image_name
            
            cmd = compose_cmd + ["up", "-d"]
            
            # docker-compose.ymlを一時的に修正する必要がある場合
            if container_name != 'llm-dev':
                print(f"📝 カスタムコンテナ名: {container_name}")
                # 通常のdocker runを使用
                run_with_docker(config, container_name, image_name)
            else:
                result = subprocess.run(cmd, env=env)
                if result.returncode == 0:
                    print("✅ コンテナ起動成功")
                    print_connection_info(container_name, config)
                else:
                    print("❌ Docker Compose起動に失敗しました")
                    print("💡 通常のDocker起動を試します...")
                    run_with_docker(config, container_name, image_name)
        else:
            print("⚠️  Docker Composeがインストールされていません")
            print("💡 通常のDocker起動を使用します...")
            run_with_docker(config, container_name, image_name)
    else:
        print("📝 docker-compose.ymlが見つかりません")
        print("💡 通常のDocker起動を使用します...")
        run_with_docker(config, container_name, image_name)

def run_with_docker(config, container_name, image_name):
    """通常のdocker runでコンテナを起動"""
    mount_path = config.get('mount_path', '/workspace')
    
    # 既存のコンテナを停止
    subprocess.run(["docker", "stop", container_name], capture_output=True)
    subprocess.run(["docker", "rm", container_name], capture_output=True)
    
    # コンテナ起動コマンド
    cmd = [
        "docker", "run",
        "--gpus", "all",
        "--name", container_name,
        "-v", f"{os.getcwd()}/workspace:{mount_path}",
        "-v", f"{os.path.expanduser('~')}/.cache/huggingface:/root/.cache/huggingface",
        "--shm-size", "16g",
        "-p", "8888:8888",
        "-p", "6006:6006",
        "-it",
        "-d",
        image_name
    ]
    
    print(f"🚀 コンテナを起動中: {container_name}")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"✅ コンテナ起動成功: {container_name}")
        print_connection_info(container_name, config)
    else:
        print("❌ コンテナ起動に失敗しました")

def print_connection_info(container_name, config):
    """接続情報を表示"""
    print(f"\n📝 接続方法:")
    print(f"  docker exec -it {container_name} bash")
    
    if config.get('jupyter'):
        print(f"\n🌐 サービス:")
        print(f"  Jupyter Lab: http://localhost:8888")
        print(f"    起動: docker exec -it {container_name} jupyter lab --ip 0.0.0.0 --allow-root --no-browser")
    
    if config.get('packages', {}).get('mlflow'):
        print(f"  MLflow: http://localhost:5000")
    
    print(f"  TensorBoard: http://localhost:6006")

def list_packages(config):
    """選択されたパッケージを表示"""
    cuda_info = CUDA_PYTORCH[config['cuda_version']]
    pytorch_version = config.get('pytorch_version', cuda_info['default'])
    
    print("\n📦 インストールされるパッケージ:")
    print("\n  [基本]")
    print(f"    ✅ PyTorch {pytorch_version} (CUDA {config['cuda_version']})")
    print(f"    ✅ Transformers {config['transformers_version']}")
    print("    ✅ NumPy, Pandas, Matplotlib")
    print("    ✅ Accelerate, Datasets, Hugging Face Hub")
    
    print("\n  [選択されたオプション]")
    for pkg, enabled in config['packages'].items():
        if enabled:
            info = PACKAGE_INFO.get(pkg, "")
            print(f"    ✅ {pkg}: {info}")
    
    if config.get('claude_code'):
        print("    ✅ Claude Code (Node.js 20 LTS)")
    
    if config.get('jupyter'):
        print("    ✅ Jupyter Lab")
    
    # 未選択のパッケージも表示
    print("\n  [未選択のオプション]")
    for pkg, enabled in config['packages'].items():
        if not enabled:
            info = PACKAGE_INFO.get(pkg, "")
            print(f"    ⬜ {pkg}: {info}")

def main():
    parser = argparse.ArgumentParser(
        description="Simple LLM Docker Builder - シンプルで実用的なLLM環境構築"
    )
    
    parser.add_argument(
        'command',
        choices=['init', 'validate', 'generate', 'build', 'run', 'all', 'list'],
        help='実行するコマンド'
    )
    
    parser.add_argument('--config', default='config.yaml', help='設定ファイル')
    parser.add_argument('--image', help='イメージ名')
    parser.add_argument('--name', help='コンテナ名')
    
    args = parser.parse_args()
    
    # initコマンド
    if args.command == 'init':
        init_config()
        return
    
    # 設定を読み込む
    if not os.path.exists(args.config):
        print(f"❌ 設定ファイルが見つかりません: {args.config}")
        print("💡 まず 'uv run build.py init' を実行してください")
        sys.exit(1)
    
    config = load_config(args.config)
    
    if args.command == 'validate':
        validate_config(config)
        print("✅ 設定ファイルは有効です")
    
    elif args.command == 'generate':
        validate_config(config)
        generate_dockerfile(config)
    
    elif args.command == 'build':
        validate_config(config)
        generate_dockerfile(config)
        build_image(config, args.image)
    
    elif args.command == 'run':
        run_container(args.image, args.name)
    
    elif args.command == 'list':
        list_packages(config)
    
    elif args.command == 'all':
        validate_config(config)
        list_packages(config)
        generate_dockerfile(config)
        image_name = build_image(config, args.image)
        run_container(image_name, args.name)
    
    print("\n✨ 完了!")

if __name__ == "__main__":
    main()