# GPU Task Spooler セットアップレポート

**実施日**: 2026-03-19（初版）、2026-03-25（パス変更・ユーザー名修正）
**対象環境**: sakura-pjt-toe（8x NVIDIA H200、Docker コンテナ 13 台）
**導入ソフトウェア**: [justanhduc/task-spooler](https://github.com/justanhduc/task-spooler) v2.0.0

---

## 背景・目的

複数ユーザーが GPU を手動管理していた（Notion DB 登録・`CUDA_VISIBLE_DEVICES` 手動指定）ため、競合やゾンビプロセスが発生していた。GPU Task Spooler を導入し、共有キューを構築した。

---

## アーキテクチャ概要

```
[コンテナ: llm-ozaki 等]          [ホスト]
  q -G 1 python train.py
    └─ setsid ts -f ──────────────── Unix ソケット ──── ts サーバー（root, systemd管理）
                                                          ├─ GPU スロット管理（8枚）
                                                          └─ RUNJOB 送信
                    ← RUNJOB + CUDA_VISIBLE_DEVICES=N ─┘
  ts クライアントがジョブを実行（クライアント側で fork・exec）
  出力は /cache/ts-queue/logs/ に保存
```

**重要**: justanhduc/task-spooler はジョブをサーバー側ではなく**クライアント側**で実行する。サーバーはスケジューリングと GPU 割り当てのみを担う。

---

## ビルド・インストール

### ビルド環境

```bash
# 依存パッケージ
sudo apt install cmake libjansson-dev

# CUDA ヘッダが標準パスにないため CUDA_HOME を明示
git clone https://github.com/justanhduc/task-spooler /tmp/task-spooler
cd /tmp/task-spooler
CUDA_HOME=/usr/local/cuda-12.8 make
sudo make install
# → /usr/local/bin/ts にインストール
```

CUDA ヘッダの実際のパス: `/usr/local/cuda-12.8/targets/x86_64-linux/include/nvml.h`

---

## 配置ファイル一覧

| パス | 説明 |
|------|------|
| `/usr/local/bin/ts` | task-spooler 本体バイナリ |
| `/usr/local/bin/q` | ラッパースクリプト（後述） |
| `/etc/systemd/system/ts-shared.service` | systemd サービス定義 |
| `/data/cache/ts-queue/.socket` | Unix ソケット（サーバーとクライアントの通信路） |
| `/data/cache/ts-queue/logs/` | ジョブ出力ログディレクトリ |

---

## 共有ソケットのパス設計

共有キャッシュ `/data/cache/` 配下に専用ディレクトリ `ts-queue/` を配置。コンテナからは `/cache/ts-queue/` としてマウントする。

| 環境 | ソケットパス | ログディレクトリ |
|------|------------|----------------|
| ホスト | `/data/cache/ts-queue/.socket` | `/data/cache/ts-queue/logs/` |
| 全コンテナ | `/cache/ts-queue/.socket` | `/cache/ts-queue/logs/` |

**変更履歴**: 初版では `/data/cache/matplotlib/` 内にソケット・ログを配置していたが、`q` の出力一覧で Output 列が `/cache/matplotl...` と表示されてしまう問題があったため、専用ディレクトリに移動した。

---

## systemd サービス

**`/etc/systemd/system/ts-shared.service`**

```ini
[Unit]
Description=GPU Task Spooler Shared Queue
After=network.target nvidia-persistenced.service

[Service]
Type=oneshot
RemainAfterExit=yes
Environment=TS_SOCKET=/data/cache/ts-queue/.socket
ExecStartPre=/bin/mkdir -p /data/cache/ts-queue/logs
ExecStartPre=/bin/chmod 1777 /data/cache/ts-queue/logs
ExecStart=/bin/bash -c '/usr/local/bin/ts -S 8 && /usr/local/bin/ts --set_logdir /cache/ts-queue/logs'
ExecStartPost=/bin/chmod 666 /data/cache/ts-queue/.socket
ExecStop=/usr/local/bin/ts -K
User=root

[Install]
WantedBy=multi-user.target
```

設計上の注意点：

- `User=root`: ソケット作成権限のため root で起動。`ExecStartPost` で `chmod 666` して全ユーザーがアクセス可能にする
- `-S 8`: GPU スロット数を 8 に設定
- `--set_logdir /cache/ts-queue/logs`: ログディレクトリの設定。コンテナ側のパス `/cache/ts-queue/logs` で登録することで、`q` の Output 列が `/cache/ts-queu...` と表示される

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ts-shared.service
```

---

## q ラッパースクリプト

**`/usr/local/bin/q`**

```bash
#!/bin/bash
export TS_SOCKET=${TS_SOCKET:-/cache/ts-queue/.socket}

# ユーザー名: $USER → HOSTNAME から抽出 (llm-xxx → xxx) → "unknown" の順にフォールバック
LABEL="${USER:-${HOSTNAME#llm-}}"
LABEL="${LABEL:-unknown}"

case "${1}" in
  ""|-l|-t|-c|-S|-K|-C|-k|-p|-o|-i|-s|-r|-w|-u|-U|-R|-T|-V|-h|-g|-M|-F|-a|-q)
    exec ts "$@"
    ;;
  *)
    setsid ts -f -L "$LABEL" "$@" &
    ;;
esac
```

設計上の注意点：

- `setsid`: ts を独立したセッションで起動。ターミナルの SIGHUP や docker exec の終了の影響を受けない
- `-f` (`should_go_background=0`): ts がジョブ完了まで自分でバックグラウンドに移行しない。`setsid` と組み合わせることで「セッション分離済みのフォアグラウンド待機」になる
- `&`: シェル側でバックグラウンド化してプロンプトをすぐに返す
- `-L "$LABEL"`: ジョブにユーザー名のラベルを付与（`q` 一覧で `[ozaki]` と表示される）
- ユーザー名の取得: `$USER` → コンテナの `HOSTNAME`（`llm-xxx` から `xxx` を抽出）→ `unknown` の順にフォールバック
- TS_SOCKET のデフォルト値: コンテナ内パス (`/cache/ts-queue/...`) をデフォルトにし、ホスト側は環境変数または `~/.bashrc` で上書き

### なぜ `-f` + `setsid` + `&` の組み合わせか

| アプローチ | docker exec 問題 | ターミナル閉じる問題 |
|-----------|----------------|-------------------|
| デフォルト（自動バックグラウンド） | docker exec 終了時に ts が kill される | ジョブ消える |
| `-f` のみ | 解決 | ターミナル閉じると SIGHUP で ts が死ぬ |
| `setsid` + `-f` + `&` | 解決（別セッション） | 解決（SIGHUP 届かない） |

---

## コンテナへの適用

### 新規コンテナ

docker-compose.yml / run.sh で自動的に以下が設定される：

```yaml
hostname: llm-${USER:-dev}    # ユーザー名の自動取得用
volumes:
  - /data/cache/ts-queue:/cache/ts-queue   # ソケットとログ
  - /usr/local/bin/ts:/usr/local/bin/ts:ro
  - /usr/local/bin/q:/usr/local/bin/q:ro
environment:
  - TS_SOCKET=/cache/ts-queue/.socket
```

### 既存コンテナの移行

既存コンテナは `/data/cache/ts-queue` のマウントを持たないため、再作成が必要。データはホスト側ボリュームに保存されているため消えない。

```bash
bash apply-ts-to-containers.sh
```

このスクリプトは各コンテナに対して `docker rm -f` → `run.sh` で再作成を行う。

適用済みコンテナ（13台）: llm-tagai, llm-yamada, llm-taguchi, llm-matsumoto, llm-okumura, llm-ka, llm-miki, llm-watanabe, llm-takahashi, llm-taiju, llm-takeda, llm-ozaki, llm-hori

---

## トラブルシューティング

### サーバー再起動

```bash
sudo systemctl restart ts-shared.service
```

### キューが壊れた・リセットしたい

```bash
export TS_SOCKET=/data/cache/ts-queue/.socket
ts -K        # サーバー停止
sudo systemctl start ts-shared.service  # 再起動（キューはリセットされる）
```

### 新しいコンテナを追加したとき

docker-compose.yml を使って起動すればバインドマウントで ts/q が自動で入る。手動起動の場合は `run.sh` を使う。

### ホスト側で q を使う場合

```bash
export TS_SOCKET=/data/cache/ts-queue/.socket
q -G 1 python train.py
```

または `~/.bashrc` に追記：

```bash
export TS_SOCKET=/data/cache/ts-queue/.socket
```
