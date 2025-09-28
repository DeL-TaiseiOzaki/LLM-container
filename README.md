## 🔧 カスタマイズ

### ベースイメージの変更

`templates/Dockerfile.j2` の最初の行を編集することで、ベースイメージを自由に変更できます。

**現在のデフォルト：**
```dockerfile
FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu22.04
```

**変更例：**

```dockerfile
# 例1: 異なるCUDAバージョンを使用（CUDA 11.8）
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# 例2: PyTorch公式イメージを使用
FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-runtime

# 例3: 軽量版（runtime版）を使用
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# 例4: CPU専用（GPU不要の場合）
FROM ubuntu:22.04
```

**注意事項**：
- ベースイメージのCUDAバージョンと `config.yaml` の `cuda_version` を**必ず一致**させてください
  - 例：ベースイメージが `cuda:11.8.0` なら `cuda_version: "11.8"`
- Ubuntu 22.04ベースを推奨（依存関係の互換性のため）
- 変更後は `make build` で再ビルドが必要です
- runtime版を使う場合、一部のパッケージ（Flash Attention等）のビルドができない場合があります