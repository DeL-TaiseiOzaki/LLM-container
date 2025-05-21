"""
src/dockerfile_generator.py

Jinja2 で Dockerfile を自動生成するモジュール
"""

from __future__ import annotations

import datetime
import os
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

from .presets import get_libraries_from_preset


# ────────────────────────────────────────────────────────────────
# 内部ユーティリティ
# ────────────────────────────────────────────────────────────────
def _cuda_suffix(cuda_version: str) -> str:
    """
    CUDA バージョン文字列を PyTorch wheel サフィックス（cu118 など）に変換
    """
    return "cu" + cuda_version.replace(".", "")


# ----------------------------------------------------------------
def generate_pytorch_install_command(config: Dict[str, Any]) -> str:
    """
    PyTorch の公式推奨インストール方法を生成
    CUDA バージョンに応じて適切なインストールコマンドを返す
    """
    cuda_version = config["base"]["cuda_version"]
    cuda_suffix = _cuda_suffix(cuda_version)
    
    # バージョン指定があればそれを使用、なければ空欄
    pt_cfg = config["deep_learning"]["pytorch"]
    version_spec = ""
    if pt_cfg.get("version") and pt_cfg["version"] != "":
        version_spec = f"=={pt_cfg['version']}"
    
    # PyTorch インストールコマンド生成
    return (
        f"pip install torch{version_spec} torchvision torchaudio "
        f"--index-url https://download.pytorch.org/whl/{cuda_suffix}"
    )

# ----------------------------------------------------------------
def prepare_libraries(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    プリセットまたはカスタム設定をフラットな dict リストに変換する。
    空またはNoneバージョンを適切に処理する。
    """
    libs: List[Dict[str, Any]] = []

    lib_cfg = config.get("libraries", {})
    if lib_cfg.get("use_preset", False):
        preset_name = lib_cfg.get("preset", "standard")
        libs.extend(get_libraries_from_preset(preset_name))
    else:
        # カテゴリ毎 (lora, data, utils ...) をまとめてフラット化
        custom_groups = lib_cfg.get("custom", {})
        for _, group_libs in custom_groups.items():
            for lib in group_libs:
                # コピーして元の辞書を変更しないようにする
                lib_copy = lib.copy()
                # 空バージョンチェック
                if "version" in lib_copy and (lib_copy["version"] is None or lib_copy["version"] == ""):
                    del lib_copy["version"]
                    # installキーを追加
                    lib_copy["install"] = True
                libs.append(lib_copy)

    # ここで除外フィルタ
    skip = {"bitsandbytes", "flash-attn", "flash_attn"}
    result = [lib for lib in libs if lib["name"] not in skip]

    return result

# ----------------------------------------------------------------
def prepare_environment_vars(config: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    ENV 行に展開する name/value ペアを返す
    """
    env_cfg = config.get("environment", {})
    custom = env_cfg.get("custom", [])
    return [{"name": item["name"], "value": item["value"]} for item in custom]


# ----------------------------------------------------------------
def get_template_path() -> str:
    """
    templates/Dockerfile.j2 の絶対パスを解決
    """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module_dir, "..", "templates", "Dockerfile.j2")


# ────────────────────────────────────────────────────────────────
# メイン: Dockerfile 生成
# ────────────────────────────────────────────────────────────────
def generate_dockerfile(config: Dict[str, Any]) -> str:
    """
    config から Jinja2 テンプレートをレンダリングして Dockerfile テキストを返す
    """
    render_cfg = dict(config)  # shallow copy

    # ライブラリの空/Noneバージョンの事前処理
    if "libraries" in render_cfg and "custom" in render_cfg["libraries"]:
        for category, items in render_cfg["libraries"]["custom"].items():
            for i, item in enumerate(items):
                if "version" in item and (item["version"] is None or item["version"] == ""):
                    render_cfg["libraries"]["custom"][category][i] = item.copy()
                    del render_cfg["libraries"]["custom"][category][i]["version"]
                    # installキーを追加して明示的に指定
                    render_cfg["libraries"]["custom"][category][i]["install"] = True
    
    # 追加メタ
    render_cfg["libraries_flat"] = prepare_libraries(config)
    render_cfg["env_vars"] = prepare_environment_vars(config)
    render_cfg["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    render_cfg["cuda_short"] = _cuda_suffix(config["base"]["cuda_version"])
    render_cfg["pytorch_install_command"] = generate_pytorch_install_command(config)

    # テンプレート読み込み & レンダリング
    template_path = get_template_path()
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(template_path)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    template = env.get_template(os.path.basename(template_path))
    
    # テンプレートのレンダリング
    dockerfile_content = template.render(**render_cfg)
    
    # 生成後のクリーンアップ：連続する複数の空行を単一の空行に置き換え
    import re
    dockerfile_content = re.sub(r'\n{3,}', '\n\n', dockerfile_content)
    
    return dockerfile_content
