.PHONY: help build run exec stop logs clean

USER ?= $(shell whoami)
BASE_DIR ?= $(shell pwd)  # デフォルトは現在のディレクトリ

help:
	@echo "🚀 Simple LLM Docker"
	@echo ""
	@echo "基本コマンド:"
	@echo "  make build         # イメージビルド"
	@echo "  make run           # コンテナ起動（現在のディレクトリ使用）"
	@echo "  make exec          # コンテナ接続"
	@echo "  make stop          # コンテナ停止"
	@echo "  make logs          # ログ表示"
	@echo "  make clean         # コンテナ削除"
	@echo ""
	@echo "カスタム起動:"
	@echo "  make run USER=ozaki                  # ozaki用（現在のディレクトリ）"
	@echo "  make run BASE_DIR=/home/ozaki        # ozaki用（特定パス）"
	@echo "  make run USER=esashi BASE_DIR=/data  # esashi用（/data配下）"

build:
	@python build.py build

run:
	@bash run.sh $(USER) $(BASE_DIR)

exec:
	@docker exec -it llm-$(USER) bash

stop:
	@docker stop llm-$(USER)

logs:
	@docker logs -f llm-$(USER)

clean:
	@docker rm -f llm-$(USER) 2>/dev/null || true