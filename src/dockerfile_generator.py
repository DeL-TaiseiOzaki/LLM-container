import os
import datetime
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
from .presets import get_libraries_from_preset

def generate_pytorch_install_command(config: Dict[str, Any]) -> str:
    """PyTorchインストールコマンドを生成する"""
    pytorch_config = config["deep_learning"]["pytorch"]
    cuda_version = config["base"]["cuda_version"]
    
    # CUDAバージョン固有のインストールが有効か
    if pytorch_config.get("cuda_specific", False):
        # CUDAバージョンからインデックスURLのサフィックスを決定
        # 例: 11.8 -> cu118, 12.1 -> cu121
        cuda_suffix = "cu" + cuda_version.replace(".", "")
        
        # 基本パッケージ
        packages = ["torch"]
        
        # 追加パッケージ
        if "extras" in pytorch_config and pytorch_config["extras"]:
            packages.extend(pytorch_config["extras"])
        
        # バージョン指定があれば追加
        version_spec = ""
        if pytorch_config.get("version"):
            version_spec = f"=={pytorch_config['version']}"
        
        # PyTorchインストールコマンド
        return f"pip install {' '.join(packages)}{version_spec} --index-url https://download.pytorch.org/whl/{cuda_suffix}"
    else:
        # 従来の方式（バージョン指定のみ）
        version = pytorch_config.get("version", "2.7.0")
        return f"pip install torch=={version}"

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
    
    # PyTorchインストールコマンドを追加
    render_config["pytorch_install_command"] = generate_pytorch_install_command(config)
    
    # テンプレートファイルからDockerfile生成
    template_dir = os.path.dirname(get_template_path())
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(os.path.basename(get_template_path()))
    
    return template.render(**render_config)