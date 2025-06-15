.PHONY: help init validate generate build run all clean

# デフォルトの設定
CONFIG ?= config.yaml
IMAGE_NAME ?= llm-env:latest
CONTAINER_NAME ?= llm-container

help:
	@echo "使用可能なコマンド:"
	@echo "  make init       - プロジェクトを初期化"
	@echo "  make validate   - 設定を検証"
	@echo "  make generate   - Dockerfileを生成"
	@echo "  make build      - Dockerイメージをビルド"
	@echo "  make run        - コンテナを起動"
	@echo "  make all        - すべての工程を実行"
	@echo "  make clean      - 生成されたファイルをクリーンアップ"

init:
	python build.py init

validate:
	python build.py validate --config $(CONFIG)

generate:
	python build.py generate --config $(CONFIG)

build: generate
	python build.py build --config $(CONFIG) --name $(IMAGE_NAME)

run:
	python build.py run --image $(IMAGE_NAME) --name $(CONTAINER_NAME)

all:
	python build.py all --config $(CONFIG) --image $(IMAGE_NAME) --container $(CONTAINER_NAME)

clean:
	rm -f Dockerfile
	docker rmi $(IMAGE_NAME) || true