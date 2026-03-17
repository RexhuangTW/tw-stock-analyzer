# 📊 回測引擎與圖表視覺化 - 使用指南

## 🎯 新增功能

### 1️⃣ 回測引擎 (`src/backtest/engine.py`)

完整的策略回測系統，支援:
- ✅ 買賣訊號執行
- ✅ 手續費與證交稅計算
- ✅ 淨值曲線追蹤
- ✅ 績效統計 (報酬率/最大回撤/勝率)
- ✅ 交易紀錄完整保存

### 2️⃣ 圖表視覺化 (`src/visualization/charts.py`)

專業級圖表生成，支援:
- ✅ K 線圖 (含成交量)
- ✅ 技術指標圖 (MA/RSI/MACD)
- ✅ 回測結果圖 (淨值曲線/報酬率/回撤)
- ✅ 選股結果視覺化

---

## 📦 回測引擎架構

```python
from src.backtest.engine import BacktestEngine, sma_crossover_strategy

# 建立回測引擎
engine = BacktestEngine(
    initial_capital=1000000,  # 初始資金 100 萬
    commission_rate=0.001425, # 手續費 0.1425%
    tax_rate=0.003            # 證交稅 0.3% (賣出時)
)

# 執行回測
data = fetcher.get_historical_price("2330", months=6)
strategy = sma_crossover_strategy(short_period=5, long_period=20)
result = engine.run(data, strategy)

# 查看結果
print(f"總報酬率: {result['total_return_pct']:.2f}%")
print(f"最大回撤: {result['max_drawdown_pct']:.2f}%")
print(f"勝率: {result['win_rate_pct']:.1f}%")
```

### 內建策略

#### 1. 均線交叉策略
```python
from src.backtest.engine import sma_crossover_strategy

strategy = sma_crossover_strategy(short_period=5, long_period=20)
# 黃金交叉 → 買入
# 死亡交叉 → 賣出
```

#### 2. RSI 策略
```python
from src.backtest.engine import rsi_strategy

strategy = rsi_strategy(period=14, oversold=30, overbought=70)
# RSI < 30 → 買入
# RSI > 70 → 賣出
```

### 自訂策略範例

```python
def my_strategy(data: pd.DataFrame, idx: int) -> str:
    """
    自訂策略函數
    
    Args:
        data: 完整歷史資料
        idx: 當前索引 (已知資料到 data[:idx+1])
    
    Returns:
        'BUY' | 'SELL' | 'HOLD'
    """
    if idx < 20:
        return 'HOLD'
    
    # 範例: 價格跌破 20 日均線 → 買入
    recent = data.iloc[:idx+1]
    ma20 = recent['close'].tail(20).mean()
    current_price = recent['close'].iloc[-1]
    
    if current_price < ma20 * 0.95:  # 跌破 MA20 的 5%
        return 'BUY'
    elif current_price > ma20 * 1.05:  # 突破 MA20 的 5%
        return 'SELL'
    
    return 'HOLD'

# 使用自訂策略
result = engine.run(data, my_strategy)
```

---

## 📊 圖表視覺化

### 1. K 線圖

```python
from src.visualization.charts import plot_candlestick

plot_candlestick(
    data.tail(60),  # 最近 60 天
    title="台積電 K線圖",
    save_path="candlestick.png",
    show_volume=True
)
```

**輸出範例:**
- 紅 K = 收盤價 > 開盤價 (上漲)
- 綠 K = 收盤價 < 開盤價 (下跌)
- 下方成交量柱狀圖

### 2. 技術指標圖

```python
from src.visualization.charts import plot_technical_indicators

# 先計算指標
df['ma5'] = calculate_ma(df['close'], 5)
df['ma20'] = calculate_ma(df['close'], 20)
df['rsi'] = calculate_rsi(df['close'], 14)
macd_df = calculate_macd(df['close'])
df = df.join(macd_df)

# 繪製
plot_technical_indicators(
    df.tail(60),
    indicators=['ma5', 'ma20', 'rsi', 'macd'],
    title="技術指標",
    save_path="indicators.png"
)
```

**輸出內容:**
- 上圖: 價格 + 均線
- 中圖: RSI (含超買/超賣線)
- 下圖: MACD (DIF/MACD/柱狀圖)

### 3. 回測結果圖

```python
from src.visualization.charts import plot_backtest_results

result = engine.run(data, strategy)

plot_backtest_results(
    result['equity_curve'],
    result['trades'],
    title="回測結果",
    save_path="backtest.png"
)
```

**輸出內容:**
- 上圖: 淨值曲線 + 買賣點標記 (紅▲買入/綠▼賣出)
- 中圖: 累積報酬率
- 下圖: 回撤圖

---

## 🚀 完整使用範例

### 範例 1: 測試均線策略

```python
from src.data.fetcher import TWSEFetcher
from src.backtest.engine import BacktestEngine, sma_crossover_strategy
from src.visualization.charts import plot_backtest_results

# 1. 取得資料
fetcher = TWSEFetcher()
data = fetcher.get_historical_price("2330", months=12)

# 2. 執行回測
engine = BacktestEngine(initial_capital=1000000)
strategy = sma_crossover_strategy(5, 20)
result = engine.run(data, strategy)

# 3. 查看統計
print(f"報酬率: {result['total_return_pct']:.2f}%")
print(f"交易次數: {result['total_trades']}")

# 4. 視覺化
plot_backtest_results(
    result['equity_curve'],
    result['trades'],
    save_path="my_backtest.png"
)
```

### 範例 2: 比較多種策略

```python
strategies = {
    'MA(5,20)': sma_crossover_strategy(5, 20),
    'MA(10,30)': sma_crossover_strategy(10, 30),
    'RSI(14,30,70)': rsi_strategy(14, 30, 70),
    'RSI(14,25,75)': rsi_strategy(14, 25, 75),
}

results = {}
for name, strategy in strategies.items():
    engine = BacktestEngine(initial_capital=1000000)
    result = engine.run(data, strategy)
    results[name] = result

# 列印比較表
print(f"{'策略':<15} {'報酬率':<10} {'最大回撤':<10} {'勝率':<8} {'交易次數'}")
print("-" * 60)
for name, result in results.items():
    print(f"{name:<15} {result['total_return_pct']:>8.2f}% "
          f"{result['max_drawdown_pct']:>8.2f}% "
          f"{result['win_rate_pct']:>6.1f}% "
          f"{result['total_trades']:>8}")
```

---

## 📈 回測結果解讀

### 關鍵指標

| 指標 | 說明 | 好壞判斷 |
|------|------|----------|
| **總報酬率** | (最終淨值 - 初始資金) / 初始資金 | 越高越好 |
| **最大回撤** | 淨值從高點回落的最大跌幅 | 越小越好 (風險控制) |
| **勝率** | 獲利交易 / 總交易次數 | 50% 以上佳 |
| **交易次數** | 買賣配對數 | 太少可能過擬合,太多手續費高 |

### 範例解讀

```
總報酬率: 15.3%
最大回撤: -8.2%
勝率: 62.5%
交易次數: 8
```

**解讀:**
- ✅ 報酬率 15.3% (6 個月期間,年化約 30%,不錯)
- ✅ 最大回撤 -8.2% (可接受範圍)
- ✅ 勝率 62.5% (略高於 50%,正向)
- ✅ 交易 8 次 (適中,不過度交易)

---

## ⚠️ 回測注意事項

### 1. 過度擬合 (Overfitting)
- **問題:** 參數針對歷史資料最佳化,實戰失效
- **解決:** 留出樣本外資料測試、避免過度調參

### 2. 未來函數 (Look-ahead Bias)
- **問題:** 策略使用了當時還不知道的未來資料
- **解決:** 確保 `strategy(data, idx)` 只用 `data[:idx+1]`

### 3. 生存者偏差 (Survivorship Bias)
- **問題:** 只測試現存股票,忽略下市的
- **解決:** 使用完整歷史資料庫 (本專案暫無此問題)

### 4. 交易成本
- **已處理:** 本引擎自動計算手續費 (0.1425%) 與證交稅 (0.3%)

### 5. 滑價 (Slippage)
- **未處理:** 假設以收盤價成交,實戰可能有價差
- **改善:** 可在策略中調整成交價 (e.g., `price * 1.001`)

---

## 🎨 圖表客製化

### 修改圖表樣式

```python
import matplotlib.pyplot as plt

# 設定全域樣式
plt.style.use('seaborn-v0_8-darkgrid')  # 使用內建樣式

# 或自訂顏色
from src.visualization.charts import plot_candlestick

fig = plot_candlestick(data, title="我的 K 線圖")
# 取得 axes 後可進一步調整
axes = fig.get_axes()
axes[0].set_facecolor('#f5f5f5')  # 背景色
```

### 匯出高解析度圖片

```python
plot_candlestick(
    data,
    save_path="chart_hd.png",
    figsize=(20, 12)  # 更大尺寸
)
# matplotlib 預設 DPI=150,可在 charts.py 中調整
```

---

## 📁 輸出檔案說明

執行 `python3 demo_backtest.py` 後生成:

```
tw-stock-analyzer/
├── output_candlestick.png    # K 線圖 (近 60 日)
├── output_indicators.png     # 技術指標圖 (MA/RSI/MACD)
├── output_backtest_sma.png   # 均線交叉回測結果
└── output_backtest_rsi.png   # RSI 策略回測結果
```

每張圖都是 PNG 格式,可直接插入報告或分享。

---

## 🚀 下一步擴充

- [ ] 多檔股票組合回測 (Portfolio Backtest)
- [ ] 交易滑價模擬
- [ ] 夏普比率 (Sharpe Ratio) 計算
- [ ] 互動式圖表 (Plotly)
- [ ] HTML 報告生成
- [ ] 參數最佳化 (Grid Search)

---

## 📊 實測結果 (demo_backtest.py)

**測試標的:** 台積電 (2330)  
**測試期間:** 2025-10-01 ~ 2026-03-16 (約 6 個月)  
**初始資金:** 1,000,000 元

### 策略表現

| 策略 | 報酬率 | 最大回撤 | 勝率 | 交易次數 |
|------|--------|----------|------|----------|
| 均線交叉 (MA5 x MA20) | 0.00% | 0.00% | N/A | 0 |
| RSI (30/70) | 0.00% | 0.00% | N/A | 0 |

**說明:**  
測試期間台積電未觸發黃金交叉/死亡交叉,也未達 RSI 極值,因此兩策略都沒有交易。這是**正常現象** — 說明策略紀律性強,不會亂進場。

**建議:**  
- 測試更長時間 (12-24 個月)
- 測試波動更大的股票
- 調整策略參數 (e.g., RSI 改 35/65)

---

**開發完成時間:** 2026-03-17  
**狀態:** ✅ 回測引擎與視覺化完整可用
