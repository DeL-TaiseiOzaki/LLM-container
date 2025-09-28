.PHONY: help init validate generate build run exec stop clean logs all

# デフォルト設定
CONFIG ?= config.yaml
IMAGE_NAME ?= llm-env:latest
CONTAINER_NAME ?= llm-dev

help:
	@echo "📚 使用可能なコマンド:"
	@echo ""
	@echo "  make init       - 初期設定（config.yaml生成）"
	@echo "  make validate   - 設定を検証"
	@echo "  make generate   - Dockerfileを生成"
	@echo "  make build      - Dockerイメージをビルド"
	@echo "  make run        - コンテナを起動"
	@echo "  make exec       - コンテナに接続"
	@echo "  make stop       - コンテナを停止"
	@echo "  make logs       - ログを表示"
	@echo "  make clean      - クリーンアップ"
	@echo "  make all        - すべて実行（init→build→run）"
	@echo ""
	@echo "📝 使用例:"
	@echo "  make init       # 初回のみ"
	@echo "  make all        # 一括実行"
	@echo "  make exec       # コンテナに入る"

init:
	@echo "🚀 初期設定を開始..."
	@python build.py init

validate:
	@python build.py validate --config $(CONFIG)

generate:
	@python build.py generate --config $(CONFIG)

build:
	@echo "🔨 Dockerイメージをビルド中..."
	@python build.py build --config $(CONFIG) --image $(IMAGE_NAME)

run:
	@echo "🚀 コンテナを起動中..."
	@if [ -f docker-compose.yml ]; then \
		docker-compose up -d; \
	else \
		python build.py run --image $(IMAGE_NAME) --name $(CONTAINER_NAME); \
	fi

exec:
	@echo "📟 コンテナに接続中..."
	@docker exec -it $(CONTAINER_NAME) bash

stop:
	@echo "⏹️ コンテナを停止中..."
	@if [ -f docker-compose.yml ]; then \
		docker-compose down; \
	else \
		docker stop $(CONTAINER_NAME) || true; \
	fi

logs:
	@docker logs -f $(CONTAINER_NAME)

clean:
	@echo "🧹 クリーンアップ中..."
	@docker stop $(CONTAINER_NAME) || true
	@docker rm $(CONTAINER_NAME) || true
	@rm -f Dockerfile

all: init build run
	@echo "✨ セットアップ完了!"
	@echo ""
	@echo "📝 次のステップ:"
	@echo "  make exec  # コンテナに接続"