#!/bin/bash
# 完整設定並啟動台股分析器

set -e  # 遇到錯誤立即停止

cd "$(dirname "$0")"

echo "📦 步驟 1/3: 安裝專案到虛擬環境..."
uv pip install -e .

echo ""
echo "✅ 步驟 2/3: 驗證模組可用性..."
uv run python -c "from src.data.fetcher import TWSEFetcher; print('✅ src 模組可正常導入')"

echo ""
echo "🚀 步驟 3/3: 啟動 Streamlit..."
uv run streamlit run app.py
