.PHONY: help build run exec stop logs status clean

# デフォルト
IMAGE ?= llm-env:latest
USER ?= $(shell whoami)
GPU ?= all
PORT ?= 0

help:
	@echo "🚀 Simple LLM Docker (Multi-User)"
	@echo ""
	@echo "使い方:"
	@echo "  make build              # イメージビルド（初回のみ）"
	@echo "  make run USER=名前      # コンテナ起動"
	@echo "  make exec USER=名前     # コンテナ接続"  
	@echo "  make stop USER=名前     # コンテナ停止"
	@echo "  make status             # 全コンテナ状態"
	@echo "  make logs USER=名前     # ログ表示"
	@echo ""
	@echo "オプション:"
	@echo "  GPU=0                   # GPU指定（デフォルト: all）"
	@echo "  PORT=10                 # ポートオフセット（デフォルト: 0）"
	@echo ""
	@echo "例:"
	@echo "  make run USER=ozaki GPU=0 PORT=0    # ozaki: GPU0, port 8888"
	@echo "  make run USER=esashi GPU=1 PORT=10  # esashi: GPU1, port 8898"

build:
	@echo "🔨 ビルド中..."
	@python build.py init
	@python build.py build --image $(IMAGE)

run:
	@chmod +x run.sh
	@./run.sh $(USER) $(GPU) $(PORT)

exec:
	@docker exec -it llm-$(USER) bash

stop:
	@docker stop llm-$(USER)

logs:
	@docker logs -f llm-$(USER)

status:
	@echo "📊 LLMコンテナ状態:"
	@docker ps -a --filter "name=llm-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

clean:
	@docker rm llm-$(USER)

clean-all:
	@docker rm $$(docker ps -aq --filter "name=llm-") 2>/dev/null || true