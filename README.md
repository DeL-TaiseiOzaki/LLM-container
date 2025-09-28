# 🚀 Simple LLM Docker

## クイックスタート

```bash
# 1. ビルド（初回のみ、10-20分）
make build

# 2. 起動
make run

# 3. 接続
make exec
```

## 含まれるもの

- **基本**: PyTorch, Transformers, NumPy, Pandas
- **推論**: vLLM, Flash Attention 2
- **学習**: TRL, Unsloth, PEFT
- **API**: OpenAI, LiteLLM
- **その他**: Weights & Biases, Claude Code

## マルチユーザー利用

```bash
# ozakiさん用
make run USER=ozaki BASE_DIR=/home/ozaki
```

## カスタマイズ

`config.yaml`を編集して必要なパッケージをON/OFF：

```yaml
packages:
  vllm: true          # 高速推論
  unsloth: false      # ← falseにすれば無効化
  wandb: true         # 実験管理
```

`templates/Dockerfile.j2`の1行目でベースイメージ変更可能：
```dockerfile
FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu22.04  # ← お好きなイメージに
```

## トラブルシューティング

### Docker権限エラー
```bash
# 解決法1: run.shを使う（自動sudo）
./run.sh ユーザー名

# 解決法2: dockerグループに追加
sudo usermod -aG docker $USER
# ログアウト→再ログイン
```

### CUDAバージョンが合わない
`config.yaml`を編集：
```yaml
cuda_version: "12.8"  # あなたのGPUに合わせて変更
```

## ライセンス

Apache License 2.0