#!/bin/bash
# 📊 台股分析器 Web UI 啟動腳本

cd "$(dirname "$0")"

echo "🚀 啟動台股分析器 Web UI..."
echo "📂 工作目錄: $(pwd)"
echo ""

# 使用 uv 執行 streamlit
uv run streamlit run app.py
