# 台股分析器 (TW Stock Analyzer)

台灣股市分析工具，支援技術指標計算、選股篩選、即時監控、策略回測與圖表視覺化。

[![Tests](https://img.shields.io/badge/tests-25%20passed-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-28%25-yellow)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)]()

## 功能

- **資料擷取** (`src/data/`): 從 TWSE API 抓取台股歷史數據
- **技術指標** (`src/indicators/`): 計算 MA、RSI、MACD、KD、布林通道
- **選股篩選** (`src/screener/`): 根據條件篩選符合策略的股票
- **即時監控** (`src/monitor/`): 監控特定股票並發送通知
- **回測引擎** (`src/backtest/`): 策略回測與績效分析 ✨
- **圖表視覺化** (`src/visualization/`): K線圖、技術指標圖、回測結果圖 ✨

## 專案結構

```
tw-stock-analyzer/
├── src/
│   ├── data/          # 資料擷取模組
│   ├── indicators/    # 技術指標計算
│   ├── screener/      # 選股篩選引擎
│   ├── monitor/       # 即時監控
│   ├── backtest/      # 回測引擎 ✨
│   └── visualization/ # 圖表視覺化 ✨
├── tests/             # 單元測試 ✅
├── config/            # 設定檔
├── demo.py            # 選股+監控示範
├── demo_backtest.py   # 回測+視覺化示範 ✨
└── README.md
```

## 使用技術

- Python 3.9+
- pandas (數據處理)
- requests (API 呼叫)
- matplotlib (圖表繪製) ✨
- plotly (互動圖表，可選) ✨
- numpy (數值計算)
- pytest (單元測試) ✅

## 快速開始

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行完整示範
python3 demo.py                # 選股 + 監控示範
python3 demo_backtest.py       # 回測 + 視覺化示範 ✨

# 執行測試
pytest tests/ -v               # 單元測試 ✅
pytest tests/ --cov=src        # 測試覆蓋率

# 單獨執行
python3 test_fetcher.py        # 測試資料擷取
python3 test_indicators.py     # 測試技術指標
```

## 開發狀態

✅ **v1.0 完成** - 核心功能完整可用 (2026-03-17)

### 已完成
- [x] 資料擷取 (TWSE API)
- [x] 技術指標 (MA/RSI/MACD/KD/BB)
- [x] 選股篩選 (3 種策略)
- [x] 即時監控
- [x] 回測引擎 (含成本計算)
- [x] 圖表視覺化 (K線/指標/回測)
- [x] 單元測試 (25 個測試,全部通過) ✅

### 待擴充
- [ ] 提高測試覆蓋率 (目前 28%)
- [ ] 更多資料源 (櫃買/Yahoo Finance)
- [ ] Discord/Telegram 通知
- [ ] 資料庫儲存
- [ ] Web UI

## 測試

```bash
# 執行所有測試
pytest tests/ -v

# 查看測試覆蓋率
pytest tests/ --cov=src --cov-report=html

# 測試特定模組
pytest tests/test_indicators.py -v
pytest tests/test_backtest.py -v
pytest tests/test_screener.py -v
```

**測試統計:**
- ✅ 25 個單元測試
- ✅ 100% 通過率
- 📊 28% 程式碼覆蓋率 (核心模組 70-100%)

## 文件

- [完整成果報告](FINAL_SUMMARY.md)
- [回測與視覺化指南](BACKTEST_VISUALIZATION_GUIDE.md)
- [視覺化成果展示](VISUAL_SUMMARY.md)

## 授權

MIT License

---

**開發者:** Claw-Agent 🦞  
**專案開始:** 2026-03-17  
**最後更新:** 2026-03-17
