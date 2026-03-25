#!/bin/bash
# 全コンテナを再作成して GPU Task Spooler の新パスを適用する
# データはホスト側ボリュームに保存されているため消えない

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINERS=$(docker ps --format "{{.Names}}" | sort)

echo "以下のコンテナを再作成します（データは消えません）:"
for CONTAINER in $CONTAINERS; do
    echo "  - $CONTAINER"
done
echo ""
read -p "続行しますか？ (y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "中断しました"
    exit 0
fi
echo ""

for CONTAINER in $CONTAINERS; do
    # コンテナ名から USER を抽出 (llm-xxx → xxx)
    USERNAME="${CONTAINER#llm-}"
    echo "=== $CONTAINER (user: $USERNAME) ==="

    docker rm -f "$CONTAINER"
    bash "$SCRIPT_DIR/run.sh" "$USERNAME"

    echo "    done"
    echo ""
done

echo "全コンテナの再作成完了"
echo "動作確認: docker exec -it <コンテナ名> bash -lc 'q'"
