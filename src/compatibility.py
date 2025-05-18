"""
バージョン互換性チェックユーティリティ
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple
from packaging.version import Version


# ────────────────────────────────────────────────────────────────
# 個別チェック関数
# ────────────────────────────────────────────────────────────────
def check_cuda_pytorch_compatibility(
    config: Dict[str, Any],
    compatibility_maps: Dict[str, Any],
) -> List[str]:
    """
    CUDA ↔ PyTorch の互換性を検証する。
    """
    # CUDA 固有 wheel を使う場合はスキップ
    if config["deep_learning"]["pytorch"].get("cuda_specific", False):
        return []

    cuda_ver = config["base"]["cuda_version"]
    pt_ver   = config["deep_learning"]["pytorch"]["version"]

    cuda_map = compatibility_maps["cuda_pytorch"]["cuda"]
    warnings: List[str] = []

    if cuda_ver not in cuda_map:
        warnings.append(f"CUDA {cuda_ver} は互換性マップに未掲載")
    elif pt_ver not in cuda_map[cuda_ver]["compatible_pytorch"]:
        compat = ", ".join(cuda_map[cuda_ver]["compatible_pytorch"])
        warnings.append(
            f"CUDA {cuda_ver} と PyTorch {pt_ver} は非互換。選択可能: {compat}"
        )

    return warnings


def check_pytorch_python_compatibility(
    config: Dict[str, Any],
    compatibility_maps: Dict[str, Any],
) -> List[str]:
    """
    PyTorch ↔ Python の互換性を検証する。
    """
    pt_ver     = config["deep_learning"]["pytorch"]["version"]
    py_ver_str = config["base"]["python_version"]

    py_map = compatibility_maps["pytorch_python"]["pytorch"]
    warnings: List[str] = []

    if pt_ver not in py_map:
        warnings.append(f"PyTorch {pt_ver} は Python 互換表に未掲載")
        return warnings

    compat_pys = py_map[pt_ver]["compatible_python"]
    if py_ver_str not in compat_pys:
        warnings.append(
            f"PyTorch {pt_ver} と Python {py_ver_str} は非互換。選択可能: {', '.join(compat_pys)}"
        )
    return warnings


def check_flash_attention_compatibility(
    config: Dict[str, Any],
    compatibility_maps: Dict[str, Any],
) -> List[str]:
    """
    Flash-Attention ↔ CUDA, PyTorch の互換性を検証する。
    """
    attn_cfg = config["deep_learning"]["attention"]
    if not attn_cfg.get("flash_attention", False):
        return []

    fa_ver   = attn_cfg["flash_attention_version"]
    cuda_ver = config["base"]["cuda_version"]
    pt_ver   = config["deep_learning"]["pytorch"]["version"]

    fa_map = compatibility_maps["flash_attention"]["flash_attention"]
    warnings: List[str] = []

    if fa_ver not in fa_map:
        warnings.append(f"Flash-Attention {fa_ver} は互換表に未掲載")
        return warnings

    fa_entry = fa_map[fa_ver]
    if cuda_ver not in fa_entry["compatible_cuda"]:
        warnings.append(
            f"Flash-Attention {fa_ver} は CUDA {cuda_ver} 非対応。対応: {', '.join(fa_entry['compatible_cuda'])}"
        )
    if pt_ver not in fa_entry["compatible_pytorch"]:
        warnings.append(
            f"Flash-Attention {fa_ver} は PyTorch {pt_ver} 非対応。対応: {', '.join(fa_entry['compatible_pytorch'])}"
        )
    return warnings


# ────────────────────────────────────────────────────────────────
# トップレベル API
# ────────────────────────────────────────────────────────────────
def validate_config(
    config: Dict[str, Any],
    compatibility_maps: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    """
    すべての互換性チェックをまとめるフロントエンド。
    戻り値: (致命的エラーなしなら True, 警告・エラー文字列リスト)
    """
    warnings: List[str] = []

    warnings += check_cuda_pytorch_compatibility(config, compatibility_maps)
    warnings += check_pytorch_python_compatibility(config, compatibility_maps)
    warnings += check_flash_attention_compatibility(config, compatibility_maps)
    # TODO: Transformers / TRL チェックを追加する

    is_valid = len([w for w in warnings if "非互換" in w]) == 0
    return is_valid, warnings
