#!/bin/bash

# mamba 初期化（.bashrc 等に追記）
mamba init -q

# Pythonバージョンを最新にアップデート（必要に応じて）
mamba update python -qy

# 全パッケージのアップデート
mamba update -qy --all

# キャッシュ等を削除
mamba clean -qafy
