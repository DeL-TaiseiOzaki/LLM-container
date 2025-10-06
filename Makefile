.PHONY: help build run exec stop logs clean down

USER ?= $(shell whoami)
BASE_DIR ?= $(shell pwd)/users/$(USER)

help:
	@echo "🚀 Simple LLM Docker"
	@echo ""
	@echo "基本コマンド:"
	@echo "  make build         # イメージビルド"
	@echo "  make run           # コンテナ起動（docker-compose使用）"
	@echo "  make exec          # コンテナ接続"
	@echo "  make stop          # コンテナ停止"
	@echo "  make logs          # ログ表示"
	@echo "  make clean         # コンテナ削除"
	@echo "  make down          # docker-compose down"
	@echo ""
	@echo "カスタム起動:"
	@echo "  make run USER=ozaki                  # ozaki用コンテナ起動"
	@echo "  make run USER=ozaki BASE_DIR=/data/ozaki  # 特定パス指定"

build:
	@python build.py build

run:
	@bash run.sh $(USER) $(BASE_DIR)

exec:
	@docker exec -it llm-$(USER) bash

stop:
	@USER=$(USER) docker compose stop

logs:
	@docker logs -f llm-$(USER)

clean:
	@USER=$(USER) docker compose down

down:
	@docker compose down