#!/bin/bash
# 📊 台股分析器 Web UI 啟動腳本

cd "$(dirname "$0")"

echo "🚀 啟動台股分析器 Web UI..."
echo "📂 工作目錄: $(pwd)"
echo ""

# 檢查是否已同步環境
if [ ! -d ".venv" ]; then
    echo "📦 首次執行，正在設定環境..."
    uv sync
    echo ""
fi

# 使用 uv run 啟動
echo "🌐 啟動 Streamlit..."
uv run streamlit run app.py
