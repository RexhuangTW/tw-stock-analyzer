# 📖 每日選股工具使用指南

## 🎯 功能說明

每日選股工具會自動執行 **6 種選股策略**，幫你找出適合買入的股票。

### 策略清單

1. **RSI 超賣** - 找出短線超賣的反彈機會
2. **黃金交叉** - 找出 MA5 突破 MA20 的趨勢轉多股
3. **動能策略** - 找出連續上漲且量能放大的強勢股
4. **量價突破** - 找出突破整理且量增的爆發股
5. **布林收縮** - 找出盤整待噴發的潛力股
6. **多因子評分** - 綜合評估找出高分股票

---

## 🚀 快速開始

### 方法 1: 手動執行 (推薦新手)

```bash
cd /Users/rex-mbp/tw-stock-analyzer

# 執行選股
./run_daily_screener.sh

# 查看結果
./view_latest_screening.sh
```

### 方法 2: 直接執行 Python

```bash
cd /Users/rex-mbp/tw-stock-analyzer
python3 daily_screener.py
```

---

## ⏰ 自動化執行

### 設定每日自動選股 (每天早上 8:30)

```bash
./setup_daily_cron.sh
```

這會設定 cron job，每週一到週五早上 8:30 自動執行選股。

### 查看 cron 設定

```bash
crontab -l
```

### 移除自動化

```bash
crontab -e
# 刪除包含 run_daily_screener.sh 的那一行
```

---

## 📊 查看結果

### 1. 終端機查看

```bash
# 查看最新結果
./view_latest_screening.sh

# 查看特定日期
cat screening_results/screening_2026-03-17.md
```

### 2. Markdown 編輯器查看

```bash
# macOS
open screening_results/screening_2026-03-17.md

# 使用 VS Code
code screening_results/screening_2026-03-17.md
```

### 3. 查看所有歷史紀錄

```bash
ls -lt screening_results/
```

---

## 🎛️ 自訂參數

編輯 `daily_screener.py` 的設定區塊：

```python
# ==================== 設定 ====================

# 台灣 50 成分股 (可自行調整股票池)
STOCK_POOL = [
    '2330', '2317', '2454', ...
]

# 參數設定
RSI_THRESHOLD = 35          # RSI 低於此值視為超賣 (可改 30 或 40)
MULTI_FACTOR_MIN = 60       # 多因子最低分數 (可改 50-70)
LOOKBACK_DAYS = 20          # 量價突破回溯天數
SQUEEZE_THRESHOLD = 0.05    # 布林通道收縮閾值
```

### 常用調整

**保守型 (降低風險):**
```python
RSI_THRESHOLD = 30          # 更嚴格的超賣標準
MULTI_FACTOR_MIN = 70       # 只選高分股
```

**積極型 (增加機會):**
```python
RSI_THRESHOLD = 40          # 放寬超賣標準
MULTI_FACTOR_MIN = 50       # 降低評分門檻
```

---

## 📋 結果解讀

### 輸出格式

```markdown
# 📊 台股選股結果 - 2026-03-17

## 1️⃣ RSI 超賣 (短線反彈)

| stock_id | rsi   | close   |
|----------|-------|---------|
| 2330     | 28.5  | 1875.0  |
| 2454     | 32.1  | 1245.0  |

## ⭐️ 重點推薦

| 股票代號 | 出現次數 |
|----------|----------|
| 2330     | 3        |  ← 出現在 3 個策略，重點關注！
| 2454     | 2        |
```

### 如何使用

1. **優先看「⭐️ 重點推薦」**
   - 出現次數越多 = 越多策略看好
   - 出現 3 次以上 = 強烈推薦

2. **依風險偏好選策略**
   - 保守: RSI 超賣 + 多因子評分
   - 穩健: 黃金交叉
   - 積極: 動能策略 + 量價突破

3. **進一步確認**
   - 用 Streamlit 查看 K 線圖
   - 檢查成交量
   - 看新聞有無利空

---

## 🎯 實戰流程

### 每日選股 SOP

```bash
# 週一到週五早上
1. 執行選股
   ./run_daily_screener.sh

2. 查看結果
   ./view_latest_screening.sh

3. 記下重點股票
   重點推薦的 2-3 檔

4. 開啟 Streamlit 確認
   python3 -m streamlit run app.py
   
5. 觀察盤中表現
   設定價格提醒

6. 決定進場時機
   突破壓力或回測支撐
```

### 週末回顧

```bash
# 週末檢視本週選股成效
ls -lt screening_results/ | head -6

# 統計勝率
# 哪些策略最準？
# 調整參數
```

---

## 🔧 進階技巧

### 1. 組合多個策略

```python
# 在 daily_screener.py 最後加入

# 範例: RSI 超賣 + 在 MA20 上方
rsi_stocks = screen_rsi_oversold(STOCK_POOL, 35)
for stock in rsi_stocks['stock_id']:
    df = fetch_data(stock)
    if df.iloc[-1]['close'] > df.iloc[-1]['ma20']:
        print(f"✅ {stock} - RSI 超賣且在月線上")
```

### 2. 整合到 Streamlit

在 `app.py` 的選股頁面加入「執行每日選股」按鈕，點擊後執行 `daily_screener.py`。

### 3. 通知整合

```python
# 在 daily_screener.py 加入通知
from src.notification.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier(bot_token="...", chat_id="...")

if hot_stocks:  # 有重點推薦股票
    message = f"📊 今日選股: {', '.join(hot_stocks.keys())}"
    notifier.send_message(message)
```

---

## 🐛 常見問題

### Q1: 執行時出現 `No module named 'src.data'`

**解決:**
```bash
cd /Users/rex-mbp/tw-stock-analyzer
python3 daily_screener.py  # 而非 python daily_screener.py
```

### Q2: 沒有任何結果

**可能原因:**
- 參數太嚴格 (降低 RSI_THRESHOLD 或 MULTI_FACTOR_MIN)
- 市場沒有符合條件的股票 (正常現象)
- API 連線問題 (檢查網路)

### Q3: 想加入自己的股票

**編輯 `daily_screener.py`:**
```python
STOCK_POOL = [
    '2330',  # 台積電
    '2454',  # 聯發科
    # 加入你想追蹤的股票
    '2881',  # 富邦金
    '6505',  # 台塑化
]
```

### Q4: cron job 沒執行

**檢查:**
```bash
# 查看 cron 日誌
tail -f screener.log

# 確認 cron 服務運行
# macOS 不需要啟動 cron，會自動運行
```

---

## 📚 延伸閱讀

- [技術分析教學](./TECHNICAL_ANALYSIS_GUIDE.md) (如果有)
- [回測驗證](./BACKTEST_GUIDE.md)
- [策略組合範例](./STRATEGY_EXAMPLES.md)

---

## 💡 使用提示

1. **不要盲目相信選股結果** - 技術分析是輔助工具
2. **永遠設定停損** - 保護資本最重要
3. **分散投資** - 不要 all-in 單一股票
4. **持續記錄** - 追蹤選股成效，改進策略
5. **保持學習** - 市場會變，策略也要跟著調整

---

**祝你選股順利！** 🦞📈
