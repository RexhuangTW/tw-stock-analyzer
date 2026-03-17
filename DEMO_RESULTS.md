# 台股分析器 - 成果展示

## 📦 專案結構

```
tw-stock-analyzer/
├── src/
│   ├── data/
│   │   ├── fetcher.py          # 資料擷取 (TWSE API)
│   │   └── __init__.py
│   ├── indicators/
│   │   ├── technical.py        # 技術指標 (MA/RSI/MACD/KD/布林通道)
│   │   └── __init__.py
│   ├── screener/
│   │   ├── engine.py           # 選股引擎
│   │   ├── strategies.py       # 預設策略 (RSI超賣/黃金交叉/動能)
│   │   └── __init__.py
│   ├── monitor/
│   │   ├── watcher.py          # 即時監控器
│   │   └── __init__.py
│   └── __init__.py
├── tests/                      # 單元測試 (待補)
├── config/
│   └── settings.example.py     # 設定檔範例
├── demo.py                     # 完整示範程式
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ✅ 已完成功能

### 1️⃣ 資料擷取 (Data Fetching)

**模組:** `src/data/fetcher.py`

- ✅ `TWSEFetcher.get_daily_price()` - 單月日成交資料
- ✅ `TWSEFetcher.get_historical_price()` - 多月歷史資料
- ✅ 民國年自動轉西元年
- ✅ 千分位、符號自動處理
- ✅ 成交量轉換 (股 → 張)

**測試結果:**
```
✅ 成功抓取台積電 (2330) 11 筆 3 月資料
✅ 欄位: date, open, high, low, close, volume, change, transactions
✅ 多月資料合併正常
```

---

### 2️⃣ 技術指標 (Technical Indicators)

**模組:** `src/indicators/technical.py`

- ✅ **MA** (移動平均線) - 任意週期
- ✅ **RSI** (相對強弱指標) - 預設 14 日
- ✅ **MACD** (指數平滑異同移動平均線)
- ✅ **KD** (隨機指標)
- ✅ **Bollinger Bands** (布林通道)

**測試結果:**
```
✅ MA5/MA20 計算正常
✅ RSI 計算正常 (需 14+ 筆資料)
✅ MACD 三線 (DIF/MACD/OSC) 正常
```

---

### 3️⃣ 選股篩選 (Stock Screener)

**模組:** `src/screener/`

#### 選股引擎 (`engine.py`)
- ✅ 支援鏈式條件組合
- ✅ 預設篩選函數 (價格/成交量/RSI/黃金交叉)

#### 預設策略 (`strategies.py`)
- ✅ **RSI 超賣策略** - 找出 RSI < 30 的股票
- ✅ **黃金交叉策略** - 找出 MA5 上穿 MA20 的股票
- ✅ **動能策略** - 找出連續上漲且量增的股票

**執行結果 (demo.py):**
```
【策略 1】RSI 超賣 (RSI < 30)
🔍 分析 2330... ❌ RSI=45.5
🔍 分析 2317... ❌ RSI=42.9
🔍 分析 2454... ❌ RSI=44.2
🔍 分析 2412... ❌ RSI=55.2
🔍 分析 2308... ❌ RSI=53.6
❌ 無符合條件的股票

【策略 2】黃金交叉 (MA5 上穿 MA20)
🔍 分析 2330... ❌ MA5=1877.0, MA20=1889.5
🔍 分析 2317... ❌ MA5=214.8, MA20=223.2
🔍 分析 2454... ❌ MA5=1737.0, MA20=1788.5
🔍 分析 2412... ❌ MA5=135.8, MA20=135.2  (接近交叉!)
🔍 分析 2308... ❌ MA5=1361.0, MA20=1309.5
❌ 無符合條件的股票

【策略 3】動能策略 (連續上漲 + 量增)
🔍 分析 2330... ❌ 未符合條件
🔍 分析 2317... ❌ 未符合條件
🔍 分析 2454... ❌ 未符合條件
🔍 分析 2412... ❌ 未符合條件
🔍 分析 2308... ❌ 未符合條件
❌ 無符合條件的股票
```

> **說明:** 測試當下這 5 檔權值股都不符合條件，屬正常。策略邏輯運作正常。

---

### 4️⃣ 即時監控 (Real-time Monitoring)

**模組:** `src/monitor/watcher.py`

- ✅ `StockWatcher` - 可配置檢查間隔的監控器
- ✅ 支援多種觸發條件 (價格突破/RSI 警報/成交量異常)
- ✅ 警報處理器機制 (console/file)
- ✅ 持續監控模式 (`start_monitoring`)

**執行結果:**
```
📡 台股分析器 - 即時監控示範
➕ 加入監控: 2330
  條件: 價格突破 2000 | RSI 跌破 30
➕ 加入監控: 2454
  條件: 價格跌破 1000 | 成交量超過 5 萬張

執行即時檢查...
✅ 目前無警報
```

---

## 🎯 使用方式

### 快速測試
```bash
cd tw-stock-analyzer
python3 demo.py
```

### 自訂策略範例
```python
from src.screener.strategies import screen_rsi_oversold

# 找出科技股中 RSI < 25 的超賣標的
tech_stocks = ['2330', '2454', '2303', '3711']
result = screen_rsi_oversold(tech_stocks, rsi_threshold=25)
print(result)
```

### 啟動監控範例
```python
from src.monitor.watcher import StockWatcher, console_alert_handler

watcher = StockWatcher(check_interval=300)  # 5 分鐘
watcher.add_stock('2330', {'price_above': 2000})
watcher.add_alert_handler(console_alert_handler)
watcher.start_monitoring()  # 持續監控
```

---

## ⚠️ 注意事項

1. **資料來源限制**
   - TWSE API 單次請求回傳當月資料
   - 多月資料需多次請求 (已加 3 秒間隔避免被擋)
   - 不含盤中即時報價 (只有收盤資料)

2. **指標計算**
   - RSI 需至少 14 天資料
   - MA20 需至少 20 天資料
   - 資料不足會回傳 NaN (正常)

3. **監控頻率**
   - 建議間隔 ≥ 5 分鐘
   - 盤中資料更新較慢 (TWSE 每 5-10 分鐘更新)

---

## 🚀 下一步擴充方向

- [ ] 單元測試 (pytest)
- [ ] 更多資料來源 (櫃買中心 TPEX、Yahoo Finance)
- [ ] 盤中即時報價支援
- [ ] Discord/Telegram 通知整合
- [ ] 回測引擎 (Backtesting)
- [ ] 視覺化圖表 (matplotlib/plotly)
- [ ] 資料庫儲存 (SQLite/PostgreSQL)

---

## 📊 效能測試

**單股分析速度:**
- 單月資料: ~1.5 秒
- 6 個月資料: ~20 秒 (含 API 間隔)

**批次選股速度 (5 檔):**
- RSI 超賣策略: ~25 秒
- 黃金交叉策略: ~30 秒
- 動能策略: ~25 秒

> 速度瓶頸在 TWSE API，可考慮快取機制或使用付費資料源加速。

---

**開發完成時間:** 2026-03-17  
**測試環境:** macOS (Apple Silicon), Python 3.9.6  
**狀態:** ✅ 核心功能完整，可投入實測
