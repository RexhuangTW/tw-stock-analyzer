#!/bin/bash
# 每日選股一鍵執行腳本

cd "$(dirname "$0")"

echo "🔍 開始執行每日選股..."
echo "📅 日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

python3 daily_screener.py

echo ""
echo "✅ 選股完成！"
echo ""
echo "📖 查看結果:"
echo "   cat screening_results/screening_$(date '+%Y-%m-%d').md"
echo ""
echo "🌐 或開啟 Streamlit 查看 K 線圖:"
echo "   python3 -m streamlit run app.py"
