#!/bin/bash
# 🤖 完整自動化系統設定

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 台股分析器 - 完整自動化系統設定"
echo "=" * 80
echo ""
echo "階段 1: 基礎自動化 ✅"
echo "階段 2: 智能助理 ✅"
echo "階段 3: 完全自主 ✅"
echo ""

# === Cron Jobs ===
echo "📅 設定 Cron Jobs..."
echo ""

CRON_JOBS="
# === 台股分析器自動化 ===

# 每天早上 8:30 - 盤前準備
30 8 * * 1-5 cd $SCRIPT_DIR && python3 smart_heartbeat.py morning >> automation.log 2>&1

# 每天下午 14:30 - 盤後整理
30 14 * * 1-5 cd $SCRIPT_DIR && python3 smart_heartbeat.py aftermarket >> automation.log 2>&1

# 每天晚上 21:00 - 晚間回顧
0 21 * * 1-5 cd $SCRIPT_DIR && python3 smart_heartbeat.py evening >> automation.log 2>&1

# 每週日 20:00 - 週回顧
0 20 * * 0 cd $SCRIPT_DIR && python3 weekly_review.py >> automation.log 2>&1

# 每週日 21:00 - 自主優化
0 21 * * 0 cd $SCRIPT_DIR && python3 smart_heartbeat.py optimize >> automation.log 2>&1
"

echo "即將加入以下 Cron Jobs:"
echo "$CRON_JOBS"
echo ""

read -p "是否繼續? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]
then
    # 備份現有 crontab
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null
    
    # 移除舊的台股分析器 cron (如果有)
    (crontab -l 2>/dev/null | grep -v "台股分析器自動化" | grep -v "$SCRIPT_DIR") > /tmp/new_crontab.txt
    
    # 加入新的 cron jobs
    echo "$CRON_JOBS" >> /tmp/new_crontab.txt
    
    # 安裝新的 crontab
    crontab /tmp/new_crontab.txt
    
    echo ""
    echo "✅ Cron Jobs 已設定"
    echo ""
    echo "📋 當前 Cron 設定:"
    crontab -l | grep -A 20 "台股分析器"
    
    echo ""
    echo "📝 日誌檔案: $SCRIPT_DIR/automation.log"
    echo ""
    echo "🔍 檢視日誌:"
    echo "  tail -f $SCRIPT_DIR/automation.log"
    
else
    echo "❌ 取消設定"
    exit 1
fi

echo ""
echo "=" * 80
echo "🎉 自動化系統設定完成！"
echo ""
echo "📅 執行時程:"
echo "  • 週一~五 08:30 - 盤前準備 (選股)"
echo "  • 週一~五 14:30 - 盤後整理"
echo "  • 週一~五 21:00 - 晚間回顧"
echo "  • 每週日 20:00 - 週回顧"
echo "  • 每週日 21:00 - 自主優化"
echo ""
echo "🧪 立即測試:"
echo "  python3 smart_heartbeat.py morning"
echo ""
echo "🔔 通知設定 (可選):"
echo "  編輯 HEARTBEAT.md 設定 Discord/Telegram"
echo ""
