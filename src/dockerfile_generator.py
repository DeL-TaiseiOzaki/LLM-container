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
    CUDA-specific wheel を使って torch / torchvision / torchaudio を一括インストール
    例:
        pip install torch==2.7.0 torchvision==2.7.0 torchaudio==2.7.0 \
            --index-url https://download.pytorch.org/whl/cu128
    """
    pt_cfg = config["deep_learning"]["pytorch"]
    cuda_ver = config["base"]["cuda_version"]
    cuda_suffix = _cuda_suffix(cuda_ver)

    version = pt_cfg.get("version", "")
    if version:
        ver_spec = f"=={version}"
    else:
        ver_spec = ""

    packages = " ".join(f"{pkg}{ver_spec}" for pkg in ("torch", "torchvision", "torchaudio"))
    return f"pip install {packages} --index-url https://download.pytorch.org/whl/{cuda_suffix}"


# ----------------------------------------------------------------
def prepare_libraries(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    プリセットまたはカスタム設定をフラットな dict リストに変換する。

    さらに bitsandbytes / flash-attn はテンプレート側で個別ビルド
    を行うため、ここでは除外して二重インストールを防ぐ。
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
            libs.extend(group_libs)

    # ここで除外フィルタ
    skip = {"bitsandbytes", "flash-attn", "flash_attn"}
    libs = [lib for lib in libs if lib["name"] not in skip]

    return libs


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
    )
    template = env.get_template(os.path.basename(template_path))

    return template.render(**render_cfg)
