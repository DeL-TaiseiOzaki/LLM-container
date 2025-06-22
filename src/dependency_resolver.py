#!/usr/bin/env python3
"""
依存関係ソルバー - ML/AIライブラリの自動バージョン解決
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional, Set
from dataclasses import dataclass
from packaging.version import Version, InvalidVersion
import copy


@dataclass
class PackageConstraint:
    """パッケージの制約条件"""
    name: str
    version_constraint: str  # ">=2.0.0", "==2.1.0", etc.
    platform_specific: bool = False
    cuda_suffix: Optional[str] = None
    reason: str = ""


@dataclass
class Resolution:
    """解決結果"""
    success: bool
    packages: Dict[str, str]  # パッケージ名 -> バージョン
    install_commands: List[str]
    warnings: List[str]
    conflicts: List[str]


class DependencyResolver:
    """依存関係解決エンジン"""
    
    def __init__(self, compatibility_maps: Dict[str, Any]):
        self.compatibility_maps = compatibility_maps
        self.resolution_cache: Dict[str, Resolution] = {}
    
    def resolve_dependencies(
        self, 
        base_config: Dict[str, Any],
        strategy: str = "stability"  # "stability", "performance", "compatibility"
    ) -> Resolution:
        """
        メイン解決メソッド
        
        Args:
            base_config: 基本設定（CUDA、Python、GPU等）
            strategy: 解決戦略
        
        Returns:
            Resolution: 解決結果
        """
        try:
            # キャッシュチェック
            cache_key = self._generate_cache_key(base_config, strategy)
            if cache_key in self.resolution_cache:
                return self.resolution_cache[cache_key]
            
            # ステップ1: 基本制約の抽出
            constraints = self._extract_base_constraints(base_config)
            
            # ステップ2: PyTorchバージョンの自動解決
            pytorch_resolution = self._resolve_pytorch_version(base_config, strategy)
            if not pytorch_resolution.success:
                return pytorch_resolution
            
            constraints.extend(pytorch_resolution.packages.items())
            
            # ステップ3: Flash Attentionの解決
            flash_attn_resolution = self._resolve_flash_attention(base_config, pytorch_resolution.packages)
            if flash_attn_resolution:
                constraints.extend(flash_attn_resolution.items())
            
            # ステップ4: Transformers生態系の解決
            transformers_resolution = self._resolve_transformers_ecosystem(
                base_config, pytorch_resolution.packages
            )
            constraints.extend(transformers_resolution.items())
            
            # ステップ5: 競合チェックと最終解決
            final_resolution = self._finalize_resolution(constraints, base_config)
            
            # キャッシュに保存
            self.resolution_cache[cache_key] = final_resolution
            
            return final_resolution
            
        except Exception as e:
            return Resolution(
                success=False,
                packages={},
                install_commands=[],
                warnings=[],
                conflicts=[f"解決中にエラーが発生しました: {str(e)}"]
            )
    
    def _resolve_pytorch_version(
        self, 
        base_config: Dict[str, Any], 
        strategy: str
    ) -> Resolution:
        """PyTorchバージョンの自動解決"""
        
        cuda_version = base_config["base"]["cuda_version"]
        python_version = base_config["base"]["python_version"]
        pytorch_preference = base_config["deep_learning"]["pytorch"].get("version", "")
        
        # CUDA互換性マップから候補を取得
        cuda_map = self.compatibility_maps["cuda_pytorch"]["cuda"]
        
        if cuda_version not in cuda_map:
            return Resolution(
                success=False,
                packages={},
                install_commands=[],
                warnings=[],
                conflicts=[f"サポートされていないCUDAバージョン: {cuda_version}"]
            )
        
        compatible_pytorch_versions = cuda_map[cuda_version]["compatible_pytorch"]
        
        # 戦略に基づいてバージョンを選択
        if pytorch_preference and pytorch_preference in compatible_pytorch_versions:
            selected_pytorch = pytorch_preference
        else:
            selected_pytorch = self._select_pytorch_by_strategy(
                compatible_pytorch_versions, strategy
            )
        
        # Python互換性チェック
        if not self._check_python_pytorch_compatibility(selected_pytorch, python_version):
            return Resolution(
                success=False,
                packages={},
                install_commands=[],
                warnings=[],
                conflicts=[f"PyTorch {selected_pytorch} はPython {python_version} と非互換"]
            )
        
        # CUDAサフィックス付きのインストール仕様を生成
        cuda_suffix = self._get_cuda_suffix(cuda_version)
        pytorch_spec = f"torch=={selected_pytorch}+{cuda_suffix}"
        torchvision_spec = f"torchvision+{cuda_suffix}"
        torchaudio_spec = f"torchaudio+{cuda_suffix}"
        
        index_url = cuda_map[cuda_version]["index_url"]
        
        install_command = (
            f"uv pip install {pytorch_spec} {torchvision_spec} {torchaudio_spec} "
            f"--index-url {index_url}"
        )
        
        return Resolution(
            success=True,
            packages={
                "torch": f"{selected_pytorch}+{cuda_suffix}",
                "torchvision": f"auto+{cuda_suffix}",
                "torchaudio": f"auto+{cuda_suffix}"
            },
            install_commands=[install_command],
            warnings=[],
            conflicts=[]
        )
    
    def _resolve_flash_attention(
        self, 
        base_config: Dict[str, Any], 
        pytorch_packages: Dict[str, str]
    ) -> Optional[Dict[str, str]]:
        """Flash Attention の解決"""
        
        # Flash Attentionが必要かチェック
        if not base_config["deep_learning"]["attention"].get("flash_attention", False):
            return None
        
        gpu_arch = base_config["gpu"]["architecture"]
        cuda_version = base_config["base"]["cuda_version"]
        pytorch_version = pytorch_packages["torch"].split("+")[0]  # CUDAサフィックスを除去
        
        flash_map = self.compatibility_maps["flash_attention"]["flash_attention"]
        
        # GPU アーキテクチャに基づく推奨バージョン
        gpu_recommendations = self.compatibility_maps["flash_attention"]["gpu_recommendations"]
        
        if gpu_arch not in gpu_recommendations:
            return {
                "flash_attention_note": f"GPU アーキテクチャ {gpu_arch} はFlash Attentionをサポートしていません"
            }
        
        recommended_version = gpu_recommendations[gpu_arch]["recommended_version"]
        
        if recommended_version is None:
            return {
                "flash_attention_alternative": "xformers"  # V100等の代替案
            }
        
        # 互換性チェック
        if recommended_version in flash_map:
            flash_entry = flash_map[recommended_version]
            
            if (cuda_version in flash_entry["compatible_cuda"] and 
                pytorch_version in flash_entry["compatible_pytorch"]):
                
                return {
                    "flash_attn": recommended_version
                }
        
        # フォールバック: 他の互換バージョンを探す
        for version, entry in flash_map.items():
            if (cuda_version in entry["compatible_cuda"] and 
                pytorch_version in entry["compatible_pytorch"]):
                return {
                    "flash_attn": version
                }
        
        return {
            "flash_attention_conflict": f"互換性のあるFlash Attentionが見つかりません"
        }
    
    def _resolve_transformers_ecosystem(
        self, 
        base_config: Dict[str, Any], 
        pytorch_packages: Dict[str, str]
    ) -> Dict[str, str]:
        """Transformers生態系の解決"""
        
        pytorch_version = pytorch_packages["torch"].split("+")[0]
        python_version = base_config["base"]["python_version"]
        
        ecosystem_map = self.compatibility_maps.get("transformers_ecosystem", {})
        
        result = {}
        
        # Transformersの解決
        if "transformers" in ecosystem_map:
            transformers_version = self._find_compatible_version(
                ecosystem_map["transformers"],
                pytorch_version,
                python_version
            )
            if transformers_version:
                result["transformers"] = transformers_version
        
        # TRLの解決（Transformersに依存）
        if "trl" in ecosystem_map and "transformers" in result:
            trl_version = self._find_compatible_trl_version(
                ecosystem_map["trl"],
                result["transformers"],
                pytorch_version
            )
            if trl_version:
                result["trl"] = trl_version
        
        # Accelerateの解決
        if "accelerate" in ecosystem_map:
            accelerate_version = self._find_compatible_version(
                ecosystem_map["accelerate"],
                pytorch_version,
                python_version
            )
            if accelerate_version:
                result["accelerate"] = accelerate_version
        
        # PEFTの解決
        if "peft" in ecosystem_map and "transformers" in result:
            peft_version = self._find_compatible_peft_version(
                ecosystem_map["peft"],
                result["transformers"],
                pytorch_version
            )
            if peft_version:
                result["peft"] = peft_version
        
        return result
    
    def _finalize_resolution(
        self, 
        constraints: List[Tuple[str, str]], 
        base_config: Dict[str, Any]
    ) -> Resolution:
        """最終的な解決とコマンド生成"""
        
        packages = dict(constraints)
        install_commands = []
        warnings = []
        conflicts = []
        
        # 競合チェック
        ecosystem_conflicts = self.compatibility_maps.get("transformers_ecosystem", {}).get("conflicts", [])
        for conflict in ecosystem_conflicts:
            conflict_packages = conflict["packages"]
            if all(pkg in packages for pkg in conflict_packages):
                warnings.append(f"パッケージの競合: {', '.join(conflict_packages)} - {conflict['reason']}")
        
        # インストールコマンドの生成
        pytorch_cmd = self._generate_pytorch_install_command(packages, base_config)
        if pytorch_cmd:
            install_commands.append(pytorch_cmd)
        
        # その他のパッケージ
        other_packages = []
        for pkg, version in packages.items():
            if not pkg.startswith(("torch", "flash_attn")):
                if version and version != "auto":
                    other_packages.append(f"{pkg}=={version}")
                else:
                    other_packages.append(pkg)
        
        if other_packages:
            install_commands.append(f"uv pip install {' '.join(other_packages)}")
        
        # Flash Attentionの特別処理
        if "flash_attn" in packages:
            flash_cmd = self._generate_flash_attention_command(packages["flash_attn"])
            install_commands.append(flash_cmd)
        
        return Resolution(
            success=True,
            packages=packages,
            install_commands=install_commands,
            warnings=warnings,
            conflicts=conflicts
        )
    
    # ========== ヘルパーメソッド ==========
    
    def _generate_cache_key(self, config: Dict[str, Any], strategy: str) -> str:
        """キャッシュキーの生成"""
        key_parts = [
            config["base"]["cuda_version"],
            config["base"]["python_version"],
            config["gpu"]["architecture"],
            config["deep_learning"]["pytorch"].get("version", "auto"),
            str(config["deep_learning"]["attention"].get("flash_attention", False)),
            strategy
        ]
        return "|".join(key_parts)
    
    def _extract_base_constraints(self, config: Dict[str, Any]) -> List[Tuple[str, str]]:
        """基本制約の抽出"""
        constraints = []
        
        # 明示的に指定されたバージョンを制約として追加
        if config["deep_learning"]["pytorch"].get("version"):
            constraints.append(("torch", config["deep_learning"]["pytorch"]["version"]))
        
        return constraints
    
    def _select_pytorch_by_strategy(self, versions: List[str], strategy: str) -> str:
        """戦略に基づいたPyTorchバージョン選択"""
        try:
            sorted_versions = sorted(versions, key=lambda v: Version(v), reverse=True)
        except InvalidVersion:
            # バージョン解析に失敗した場合は文字列ソート
            sorted_versions = sorted(versions, reverse=True)
        
        if strategy == "performance" or strategy == "latest":
            return sorted_versions[0]  # 最新
        elif strategy == "compatibility":
            return sorted_versions[-1]  # 最古
        else:  # "stability"
            # 安定版を選択（2.5.x系統を優先）
            for version in sorted_versions:
                if version.startswith("2.5"):
                    return version
            return sorted_versions[len(sorted_versions) // 2]  # 中間
    
    def _get_cuda_suffix(self, cuda_version: str) -> str:
        """CUDAサフィックスの生成"""
        return f"cu{cuda_version.replace('.', '')}"
    
    def _check_python_pytorch_compatibility(self, pytorch_version: str, python_version: str) -> bool:
        """Python-PyTorch互換性チェック"""
        python_map = self.compatibility_maps.get("pytorch_python", {}).get("pytorch", {})
        
        if pytorch_version in python_map:
            compatible_pythons = python_map[pytorch_version]["compatible_python"]
            return python_version in compatible_pythons
        
        return True  # 不明な場合は互換とみなす
    
    def _find_compatible_version(
        self, 
        package_map: Dict[str, Any], 
        pytorch_version: str, 
        python_version: str
    ) -> Optional[str]:
        """互換性のあるバージョンを検索"""
        
        for version, requirements in package_map.items():
            # PyTorch要件チェック
            if "requires_pytorch" in requirements:
                pytorch_req = requirements["requires_pytorch"]
                if not self._version_satisfies(pytorch_version, pytorch_req):
                    continue
            
            # Python要件チェック
            if "requires_python" in requirements:
                python_req = requirements["requires_python"]
                if not self._version_satisfies(python_version, python_req):
                    continue
            
            # ステータスチェック（deprecatedは避ける）
            if requirements.get("status") == "deprecated":
                continue
            
            return version
        
        return None
    
    def _find_compatible_trl_version(
        self, 
        trl_map: Dict[str, Any], 
        transformers_version: str, 
        pytorch_version: str
    ) -> Optional[str]:
        """TRLバージョンの検索（Transformers要件を考慮）"""
        
        for version, requirements in trl_map.items():
            # Transformers要件チェック
            if "requires_transformers" in requirements:
                transformers_req = requirements["requires_transformers"]
                if not self._version_satisfies(transformers_version, transformers_req):
                    continue
            
            # PyTorch要件チェック
            if "requires_pytorch" in requirements:
                pytorch_req = requirements["requires_pytorch"]
                if not self._version_satisfies(pytorch_version, pytorch_req):
                    continue
            
            return version
        
        return None
    
    def _find_compatible_peft_version(
        self, 
        peft_map: Dict[str, Any], 
        transformers_version: str, 
        pytorch_version: str
    ) -> Optional[str]:
        """PEFTバージョンの検索（Transformers要件を考慮）"""
        
        for version, requirements in peft_map.items():
            # Transformers要件チェック
            if "requires_transformers" in requirements:
                transformers_req = requirements["requires_transformers"]
                if not self._version_satisfies(transformers_version, transformers_req):
                    continue
            
            # PyTorch要件チェック
            if "requires_pytorch" in requirements:
                pytorch_req = requirements["requires_pytorch"]
                if not self._version_satisfies(pytorch_version, pytorch_req):
                    continue
            
            return version
        
        return None
    
    def _version_satisfies(self, version: str, requirement: str) -> bool:
        """バージョン要件の満足チェック"""
        try:
            actual_version = Version(version)
            
            # 簡単な要件解析（">=" のみサポート）
            if requirement.startswith(">="):
                required_version = Version(requirement[2:])
                return actual_version >= required_version
            elif requirement.startswith("=="):
                required_version = Version(requirement[2:])
                return actual_version == required_version
            elif requirement.startswith(">"):
                required_version = Version(requirement[1:])
                return actual_version > required_version
            else:
                return True  # 不明な場合は満足とみなす
                
        except InvalidVersion:
            return True
    
    def _generate_pytorch_install_command(self, packages: Dict[str, str], config: Dict[str, Any]) -> Optional[str]:
        """PyTorchインストールコマンドの生成"""
        
        cuda_version = config["base"]["cuda_version"]
        
        pytorch_packages = []
        for pkg_name in ["torch", "torchvision", "torchaudio"]:
            if pkg_name in packages:
                pytorch_packages.append(packages[pkg_name])
        
        if not pytorch_packages:
            return None
        
        # インデックスURLの取得
        cuda_map = self.compatibility_maps["cuda_pytorch"]["cuda"]
        index_url = cuda_map[cuda_version]["index_url"]
        
        return f"uv pip install {' '.join(pytorch_packages)} --index-url {index_url}"
    
    def _generate_flash_attention_command(self, version: str) -> str:
        """Flash Attentionインストールコマンドの生成"""
        return f"MAX_JOBS=4 uv pip install flash-attn=={version} --no-build-isolation"


# ========== 便利関数 ==========

def auto_resolve_config(partial_config: Dict[str, Any], compatibility_maps: Dict[str, Any]) -> Dict[str, Any]:
    """部分設定から完全設定を自動生成"""
    
    resolver = DependencyResolver(compatibility_maps)
    resolution = resolver.resolve_dependencies(partial_config)
    
    if not resolution.success:
        raise ValueError(f"依存関係解決に失敗: {', '.join(resolution.conflicts)}")
    
    # 元の設定に解決結果をマージ
    result_config = copy.deepcopy(partial_config)
    
    # PyTorchバージョンを更新
    if "torch" in resolution.packages:
        torch_version = resolution.packages["torch"].split("+")[0]
        result_config["deep_learning"]["pytorch"]["version"] = torch_version
    
    # Flash Attentionバージョンを更新
    if "flash_attn" in resolution.packages:
        result_config["deep_learning"]["attention"]["flash_attention_version"] = resolution.packages["flash_attn"]
    
    return result_config


def print_resolution_report(resolution: Resolution) -> None:
    """解決結果のレポート出力"""
    
    print("🔧 依存関係解決結果")
    print("=" * 50)
    
    if resolution.success:
        print("✅ 解決成功")
        
        print("\n📦 解決されたパッケージ:")
        for package, version in resolution.packages.items():
            print(f"  {package}: {version}")
        
        print("\n💻 インストールコマンド:")
        for cmd in resolution.install_commands:
            print(f"  {cmd}")
        
        if resolution.warnings:
            print("\n⚠️  警告:")
            for warning in resolution.warnings:
                print(f"  - {warning}")
    
    else:
        print("❌ 解決失敗")
        
        if resolution.conflicts:
            print("\n🔴 競合:")
            for conflict in resolution.conflicts:
                print(f"  - {conflict}")
    
    print("=" * 50)