#!/bin/bash
# 快速查看最新的選股結果

cd "$(dirname "$0")"

LATEST_FILE=$(ls -t screening_results/screening_*.md 2>/dev/null | head -1)

if [ -z "$LATEST_FILE" ]; then
    echo "❌ 找不到選股結果"
    echo "請先執行: ./run_daily_screener.sh"
    exit 1
fi

echo "📄 最新選股結果: $LATEST_FILE"
echo ""
echo "========================================"
cat "$LATEST_FILE"
echo "========================================"
echo ""
echo "💡 提示:"
echo "  - 使用 less 查看: less $LATEST_FILE"
echo "  - 使用編輯器: open $LATEST_FILE"
