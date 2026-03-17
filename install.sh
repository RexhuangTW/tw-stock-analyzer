#!/bin/bash
# 安裝台股分析器到 uv 虛擬環境

cd "$(dirname "$0")"

echo "📦 安裝專案到虛擬環境..."
echo "目錄: $(pwd)"
echo ""

uv pip install -e .

echo ""
echo "✅ 安裝完成！"
echo ""
echo "驗證安裝..."
uv run python -c "from src.data.fetcher import TWSEFetcher; print('✅ src 模組可正常使用')"
