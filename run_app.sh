#!/bin/bash
# 📊 台股分析器 Web UI 啟動腳本

cd "$(dirname "$0")"

echo "🚀 啟動台股分析器 Web UI..."
echo "📂 工作目錄: $(pwd)"
echo ""

# 設定 PYTHONPATH 確保可以找到 src 模組
export PYTHONPATH="$(pwd):$PYTHONPATH"

# 檢查 streamlit 是否安裝
if ! command -v streamlit &> /dev/null; then
    echo "❌ streamlit 未安裝在 PATH 中，嘗試使用 python3 -m streamlit..."
    python3 -m streamlit run app.py
else
    streamlit run app.py
fi
