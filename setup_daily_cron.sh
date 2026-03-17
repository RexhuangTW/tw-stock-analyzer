#!/bin/bash
# 設定每日自動選股 (cron job)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCREENER_SCRIPT="$SCRIPT_DIR/run_daily_screener.sh"

echo "📅 設定每日自動選股任務"
echo "位置: $SCREENER_SCRIPT"
echo ""

# 建立 cron job (每天早上 8:30 執行)
CRON_CMD="30 8 * * 1-5 $SCREENER_SCRIPT >> $SCRIPT_DIR/screener.log 2>&1"

echo "將加入以下 cron job:"
echo "$CRON_CMD"
echo ""
echo "時間: 每週一到週五早上 8:30"
echo "日誌: $SCRIPT_DIR/screener.log"
echo ""

read -p "是否繼續? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # 加入 cron
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✅ Cron job 已設定"
    echo ""
    echo "查看目前的 cron jobs:"
    crontab -l
else
    echo "❌ 取消設定"
fi
