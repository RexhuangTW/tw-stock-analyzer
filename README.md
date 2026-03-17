# 台股分析器 (TW Stock Analyzer)

台灣股市分析工具，支援技術指標計算、選股篩選、即時監控、策略回測與圖表視覺化。

[![Tests](https://img.shields.io/badge/tests-25%20passed-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-16%25-yellow)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)]()
[![Version](https://img.shields.io/badge/version-1.5-blue)]()

## ✨ 功能特色

- **📊 Web UI** - Streamlit 互動式介面 (新增!)
- **📈 資料擷取** - TWSE API + Yahoo Finance (台股/美股/全球)
- **🔢 技術指標** - 15+ 種指標 (基礎 + 進階)
- **🔍 選股篩選** - 8 種策略 (RSI/均線/量價/多因子)
- **📡 即時監控** - 可設定觸發條件與警報
- **🔄 策略回測** - 完整回測引擎 (含成本計算)
- **📊 視覺化** - 靜態圖表 + 互動式圖表 (Plotly)
- **🔔 通知系統** - Discord + Telegram
- **⚡ 快取機制** - 提升資料擷取速度

## 🚀 快速開始

### 安裝

```bash
git clone https://github.com/RexhuangTW/tw-stock-analyzer.git
cd tw-stock-analyzer
pip install -r requirements.txt
```

### Web UI (推薦!)

```bash
streamlit run app.py
```

然後在瀏覽器開啟 http://localhost:8501

### 命令列使用

```bash
# 選股 + 監控
python3 demo.py

# 回測 + 圖表
python3 demo_backtest.py

# 互動式圖表
python3 demo_interactive.py

# 進階選股策略
python3 demo_advanced_screening.py
```

## 📦 專案結構

```
tw-stock-analyzer/
├── app.py ✨                    # Streamlit Web UI
├── src/
│   ├── data/                   # 資料擷取 (TWSE + Yahoo)
│   ├── indicators/             # 技術指標 (基礎 + 進階)
│   ├── screener/               # 選股策略
│   ├── monitor/                # 即時監控
│   ├── backtest/               # 回測引擎
│   ├── notification/ ✨         # Discord + Telegram
│   └── visualization/ ✨        # 圖表 (matplotlib + Plotly)
├── tests/                      # 單元測試 (25 個)
├── demo_*.py                   # 示範程式
├── README.md
├── ROADMAP.md ✨               # 開發路線圖
└── TEST_REPORT.md ✨           # 測試報告
```

## 🎯 功能清單

### 資料來源
- ✅ TWSE (台灣證券交易所)
- ✅ Yahoo Finance (全球市場)
- ✅ 即時報價 (延遲 15-20 分鐘)
- ✅ 基本面資訊

### 技術指標
**基礎指標:**
- MA (移動平均線)
- RSI (相對強弱指標)
- MACD (指數平滑異同移動平均線)
- KD (隨機指標)
- Bollinger Bands (布林通道)

**進階指標:**
- ATR (真實波動幅度)
- OBV (能量潮)
- CCI (商品通道指數)
- Williams %R (威廉指標)
- VWAP (成交量加權均價)
- ADX (平均趨向指數)
- Ichimoku (一目均衡表)
- Fibonacci Retracement (費波那契回調)

### 選股策略
**基礎策略:**
- RSI 超賣/超買
- 黃金交叉/死亡交叉
- 動能策略 (連續上漲+量增)

**進階策略:**
- 量價突破
- 布林通道收縮
- OBV 背離
- 多因子綜合評分

### 視覺化
- K 線圖 (含成交量)
- 技術指標圖 (多圖組合)
- 回測結果圖 (淨值/報酬/回撤)
- 互動式圖表 (Plotly，可縮放拖曳)

## 📊 使用範例

### Web UI

最簡單的使用方式：
```bash
streamlit run app.py
```

### Python API

```python
from src.data.fetcher import TWSEFetcher
from src.indicators.technical import calculate_ma, calculate_rsi
from src.screener.strategies import screen_rsi_oversold

# 取得資料
fetcher = TWSEFetcher()
df = fetcher.get_historical_price("2330", months=3)

# 計算指標
df['ma20'] = calculate_ma(df['close'], 20)
df['rsi'] = calculate_rsi(df['close'], 14)

# 選股
stocks = ['2330', '2317', '2454', '2412', '2308']
result = screen_rsi_oversold(stocks, rsi_threshold=30)
print(result)
```

### 回測範例

```python
from src.backtest.engine import BacktestEngine, sma_crossover_strategy

engine = BacktestEngine(initial_capital=1000000)
strategy = sma_crossover_strategy(5, 20)
result = engine.run(data, strategy)

print(f"報酬率: {result['total_return_pct']:.2f}%")
print(f"最大回撤: {result['max_drawdown_pct']:.2f}%")
```

## 🧪 測試

```bash
# 執行所有測試
pytest tests/ -v

# 查看測試覆蓋率
pytest tests/ --cov=src --cov-report=html

# 測試特定模組
pytest tests/test_indicators.py -v
```

**測試狀態:** ✅ 25/25 通過

## 🔔 通知設定

### Discord

```python
from src.notification.discord_notifier import DiscordNotifier

notifier = DiscordNotifier(webhook_url="YOUR_WEBHOOK_URL")
notifier.send_alert("2330", "BUY", "突破 2000 元!")
```

### Telegram

```python
from src.notification.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier(
    bot_token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID"
)
notifier.send_alert("2330", "SELL", "跌破支撐!")
```

## 📚 文件

- [開發路線圖](ROADMAP.md) - 未來規劃與擴充方向
- [測試報告](TEST_REPORT.md) - 完整測試驗證結果
- [最終總結](FINAL_SUMMARY.md) - v1.0 成果報告

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 🙏 致謝

- 資料來源: TWSE, Yahoo Finance
- 技術棧: Python, pandas, Plotly, Streamlit

---

**開發者:** Claw-Agent 🦞  
**版本:** v1.5  
**最後更新:** 2026-03-17

**GitHub:** https://github.com/RexhuangTW/tw-stock-analyzer
