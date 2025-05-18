#!/usr/bin/env python3
from typing import Dict, Any, List, Tuple

def check_cuda_pytorch_compatibility(
    config: Dict[str, Any], 
    compatibility_maps: Dict[str, Any]
) -> List[str]:
    """CUDA-PyTorch互換性チェック"""
    cuda_version = config["base"]["cuda_version"]
    pytorch_version = config["deep_learning"]["pytorch"]["version"]
    
    warnings = []
    cuda_map = compatibility_maps["cuda_pytorch"]["cuda"]
    
    if cuda_version not in cuda_map:
        warnings.append(f"警告: CUDA {cuda_version} は互換性マップに含まれていません。互換性が保証されません。")
    elif pytorch_version not in cuda_map[cuda_version]["compatible_pytorch"]:
        compatible_versions = cuda_map[cuda_version]["compatible_pytorch"]
        warnings.append(
            f"警告: CUDA {cuda_version} と PyTorch {pytorch_version} の組み合わせは互換性がありません。"
            f"利用可能な PyTorch バージョン: {compatible_versions}"
        )
    
    return warnings

def check_pytorch_python_compatibility(
    config: Dict[str, Any], 
    compatibility_maps: Dict[str, Any]
) -> List[str]:
    """PyTorch-Python互換性チェック"""
    pytorch_version = config["deep_learning"]["pytorch"]["version"]
    python_version = config["base"]["python_version"]
    
    warnings = []
    pytorch_map = compatibility_maps["pytorch_python"]["pytorch"]
    
    if pytorch_version not in pytorch_map:
        warnings.append(f"警告: PyTorch {pytorch_version} は互換性マップに含まれていません。互換性が保証されません。")
    elif python_version not in pytorch_map[pytorch_version]["compatible_python"]:
        compatible_versions = pytorch_map[pytorch_version]["compatible_python"]
        warnings.append(
            f"警告: PyTorch {pytorch_version} と Python {python_version} の組み合わせは互換性がありません。"
            f"利用可能な Python バージョン: {compatible_versions}"
        )
    
    return warnings

def check_flash_attention_compatibility(
    config: Dict[str, Any], 
    compatibility_maps: Dict[str, Any]
) -> List[str]:
    """Flash Attention互換性チェック"""
    if not config["deep_learning"]["attention"]["flash_attention"]:
        return []
    
    cuda_version = config["base"]["cuda_version"]
    pytorch_version = config["deep_learning"]["pytorch"]["version"]
    flash_version = config["deep_learning"]["attention"]["flash_attention_version"]
    
    warnings = []
    flash_map = compatibility_maps["flash_attention"]["flash_attention"]
    
    if flash_version not in flash_map:
        warnings.append(f"警告: Flash Attention {flash_version} は互換性マップに含まれていません。互換性が保証されません。")
    else:
        if cuda_version not in flash_map[flash_version]["compatible_cuda"]:
            compatible_cuda = flash_map[flash_version]["compatible_cuda"]
            warnings.append(
                f"警告: Flash Attention {flash_version} と CUDA {cuda_version} の組み合わせは互換性がありません。"
                f"利用可能な CUDA バージョン: {compatible_cuda}"
            )
        
        if pytorch_version not in flash_map[flash_version]["compatible_pytorch"]:
            compatible_pytorch = flash_map[flash_version]["compatible_pytorch"]
            warnings.append(
                f"警告: Flash Attention {flash_version} と PyTorch {pytorch_version} の組み合わせは互換性がありません。"
                f"利用可能な PyTorch バージョン: {compatible_pytorch}"
            )
    
    return warnings

def validate_config(
    config: Dict[str, Any], 
    compatibility_maps: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """設定の妥当性をチェックし、互換性を確認する"""
    warnings = []
    
    # CUDA-PyTorch互換性チェック
    warnings.extend(check_cuda_pytorch_compatibility(config, compatibility_maps))
    
    # PyTorch-Python互換性チェック
    warnings.extend(check_pytorch_python_compatibility(config, compatibility_maps))
    
    # Flash Attention互換性チェック
    warnings.extend(check_flash_attention_compatibility(config, compatibility_maps))
    
    # GPUの設定チェック
    if config["gpu"]["multi_node"] and config["gpu"]["nodes"] < 2:
        warnings.append(f"警告: マルチノードが有効ですが、ノード数が {config['gpu']['nodes']} になっています。2以上を指定してください。")
    
    # 警告があるかどうかを返す
    has_warnings = len(warnings) > 0
    
    return (not has_warnings, warnings)