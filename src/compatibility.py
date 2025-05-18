from typing import Dict, Any, List, Tuple

def check_cuda_pytorch_compatibility(
    config: Dict[str, Any], 
    compatibility_maps: Dict[str, Any]
    ) -> List[str]:
    """CUDA-PyTorch互換性チェック"""
    # CUDAバージョン特有のインストールが有効なら、互換性チェックをスキップ
    if config["deep_learning"]["pytorch"].get("cuda_specific", False):
        return []
    
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