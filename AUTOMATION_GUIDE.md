# 🤖 完整自動化系統指南

## 🎯 三階段自動化

### 階段 1: 基礎自動化 ✅
- Cron 定時執行
- 每日選股自動化
- 結果儲存

### 階段 2: 智能助理 ✅
- 自動判斷時段執行任務
- 主動通知重要事項
- 記憶整理與回顧

### 階段 3: 完全自主 ✅
- 自動分析策略表現
- 自主調整參數
- 學習改進機制

---

## 🚀 快速開始

### 一鍵安裝

```bash
cd /Users/rex-mbp/tw-stock-analyzer
git pull
./setup_automation.sh
```

這會設定所有 Cron Jobs 和自動化任務。

---

## 📅 執行時程

| 時間 | 任務 | 腳本 | 說明 |
|------|------|------|------|
| **週一~五 08:30** | 盤前準備 | `smart_heartbeat.py morning` | 執行選股、檢查 TODO、發送通知 |
| **週一~五 14:30** | 盤後整理 | `smart_heartbeat.py aftermarket` | 記錄盤勢、更新 memory |
| **週一~五 21:00** | 晚間回顧 | `smart_heartbeat.py evening` | 生成日報、規劃明天 |
| **每週日 20:00** | 週回顧 | `weekly_review.py` | 統計成效、整理 memory、更新 MEMORY.md |
| **每週日 21:00** | 自主優化 | `smart_heartbeat.py optimize` | 分析策略、調整參數 |

---

## 📋 功能詳解

### 1. 早上例行任務 (08:30)

**執行項目:**
- ✅ 檢查是否已執行今日選股
- ✅ 執行 `daily_screener.py`
- ✅ 分析選股結果
- ✅ 檢查是否有重點推薦 (3+ 策略)
- ✅ 檢查 TODO.md 今日待辦
- ✅ 整理昨日 memory

**通知條件:**
- 選股有重點推薦股票
- TODO 有今日 deadline
- 市場有重大變化

**輸出:**
- `screening_results/screening_YYYY-MM-DD.md`
- `daily_report_YYYY-MM-DD.md` (如有通知)
- Console 輸出到 `automation.log`

---

### 2. 盤後整理 (14:30)

**執行項目:**
- ✅ 記錄今日盤勢
- ✅ 建立/更新當日 memory 檔案
- ✅ 追蹤選股股票表現 (未來實作)

**輸出:**
- `memory/YYYY-MM-DD.md`

---

### 3. 晚間回顧 (21:00)

**執行項目:**
- ✅ 生成每日總結
- ✅ 整理今日筆記
- ✅ 規劃明日待辦

**輸出:**
- `daily_summary_YYYY-MM-DD.md`

---

### 4. 每週回顧 (週日 20:00)

**執行項目:**
- ✅ 統計本週選股執行天數
- ✅ 整理每日 memory
- ✅ 生成週報
- ✅ 更新 MEMORY.md 長期記憶

**輸出:**
- `weekly_review_YYYY-W##.md`
- 更新 `MEMORY.md`

---

### 5. 自主優化 (週日 21:00)

**執行項目:**
- ✅ 分析各策略勝率 (需累積數據)
- ✅ 自動調整 RSI_THRESHOLD
- ✅ 自動調整 MULTI_FACTOR_MIN
- ✅ 記錄調整歷史

**邏輯範例:**
```python
# RSI 策略
if 勝率 < 40% and 樣本數 >= 10:
    降低 threshold (更嚴格) → 提高品質
elif 勝率 > 70%:
    提高 threshold (放寬) → 增加機會

# 多因子評分
if 勝率 < 40%:
    提高最低分數 → 更嚴格
elif 勝率 > 70%:
    降低最低分數 → 放寬
```

**輸出:**
- 更新 `heartbeat_state.json`
- 記錄到當日 memory

---

## 🔔 通知系統

### 設定 Discord (可選)

編輯 `HEARTBEAT.md`:
```markdown
## 🔔 通知設定

**Discord:**
- Webhook URL: https://discord.com/api/webhooks/YOUR_WEBHOOK
```

在 `smart_heartbeat.py` 加入:
```python
from src.notification.discord_notifier import DiscordNotifier

notifier = DiscordNotifier(webhook_url="...")
notifier.send_message("📊 今日選股有重點推薦！")
```

### 設定 Telegram (可選)

```python
from src.notification.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier(
    bot_token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID"
)
notifier.send_message("...")
```

---

## 📊 狀態追蹤

### heartbeat_state.json

```json
{
  "last_screening": "2026-03-17",
  "last_review": null,
  "last_notification": "2026-03-17",
  "screening_success_rate": 0.65,
  "total_screenings": 45,
  "parameters": {
    "rsi_threshold": 30,      // 自動調整
    "multi_factor_min": 65,   // 自動調整
    "lookback_days": 20
  },
  "strategy_performance": {
    "rsi_oversold": {
      "win_rate": 0.72,
      "trades": 15
    },
    "golden_cross": {
      "win_rate": 0.58,
      "trades": 12
    }
  }
}
```

---

## 🔧 手動執行

### 測試早上任務
```bash
python3 smart_heartbeat.py morning
```

### 測試盤後整理
```bash
python3 smart_heartbeat.py aftermarket
```

### 測試週回顧
```bash
python3 weekly_review.py
```

### 測試自主優化
```bash
python3 smart_heartbeat.py optimize
```

---

## 📝 查看結果

### 查看選股結果
```bash
./view_latest_screening.sh
```

### 查看自動化日誌
```bash
tail -f automation.log
```

### 查看狀態
```bash
cat heartbeat_state.json | python3 -m json.tool
```

### 查看週報
```bash
ls -lt ~/. openclaw/workspace/weekly_review_*.md | head -5
```

---

## 🐛 故障排除

### Cron 沒有執行

**檢查 Cron 服務:**
```bash
# macOS - cron 應該自動運行
ps aux | grep cron

# 查看 cron 列表
crontab -l
```

**檢查日誌:**
```bash
tail -50 automation.log
```

### 選股失敗

**手動執行測試:**
```bash
cd /Users/rex-mbp/tw-stock-analyzer
python3 daily_screener.py
```

**檢查錯誤訊息:**
```bash
grep "ERROR\|錯誤" automation.log
```

### 通知沒收到

**檢查通知設定:**
- Discord Webhook URL 是否正確?
- Telegram Bot Token 是否有效?
- 是否有觸發通知條件?

---

## 📈 效能監控

### 每週檢查清單

- [ ] 查看週報統計
- [ ] 檢查選股執行率 (應該 5/5)
- [ ] 查看自動調整記錄
- [ ] 驗證通知是否正常

### 每月檢查

- [ ] 統計選股勝率
- [ ] 分析哪些策略最有效
- [ ] 檢討自主優化成效
- [ ] 調整自動化邏輯 (如需要)

---

## 💡 進階客製化

### 修改執行時間

編輯 Cron:
```bash
crontab -e

# 改為早上 8:00
0 8 * * 1-5 cd ... && python3 smart_heartbeat.py morning
```

### 修改選股參數

編輯 `daily_screener.py`:
```python
RSI_THRESHOLD = 30  # 改為更嚴格
MULTI_FACTOR_MIN = 70  # 只選高分股
```

### 修改自主優化邏輯

編輯 `smart_heartbeat.py` 的 `autonomous_optimization()` 函數。

---

## 🎓 最佳實踐

1. **先累積 2 週數據** 再啟用自主優化
2. **定期檢查日誌** 確保運行正常
3. **每週查看週報** 了解系統表現
4. **手動驗證參數調整** 不要完全依賴自動化
5. **保留原始參數** 作為備份

---

## 📚 相關文件

- [每日選股工具](./DAILY_SCREENER_GUIDE.md)
- [技術分析教學](./TECHNICAL_ANALYSIS_GUIDE.md) (如果有)
- [HEARTBEAT.md](../HEARTBEAT.md)

---

**自動化系統已就緒！** 🤖

現在你的台股分析器會：
- ✅ 每天早上自動選股
- ✅ 整理記憶與報告
- ✅ 每週統計回顧
- ✅ 自主學習優化

**享受智能助理帶來的便利！** 🦞📈
