"""互動式圖表與通知示範"""
from src.data.fetcher import TWSEFetcher
from src.indicators.technical import calculate_ma, calculate_rsi, calculate_macd
from src.visualization.plotly_charts import (
    create_candlestick_chart,
    create_technical_chart,
    create_backtest_chart
)
from src.backtest.engine import BacktestEngine, sma_crossover_strategy

print("=" * 60)
print("📊 互動式圖表示範")
print("=" * 60)

# 取得資料
print("\n📡 抓取台積電資料...")
fetcher = TWSEFetcher()
df = fetcher.get_historical_price("2330", months=3)

print(f"✅ 取得 {len(df)} 筆資料")

# 計算指標
print("\n📈 計算技術指標...")
df['ma5'] = calculate_ma(df['close'], 5)
df['ma20'] = calculate_ma(df['close'], 20)
df['ma60'] = calculate_ma(df['close'], 60)
df['rsi'] = calculate_rsi(df['close'], 14)
macd_df = calculate_macd(df['close'])
df = df.join(macd_df)

# 1. K 線圖 (含均線)
print("\n📊 生成互動式 K 線圖...")
fig1 = create_candlestick_chart(
    df.tail(60),
    title="台積電 (2330) 互動式 K 線圖",
    show_volume=True,
    indicators={'MA5': df['ma5'].tail(60), 'MA20': df['ma20'].tail(60)}
)
fig1.write_html("interactive_candlestick.html")
print("✅ 儲存至 interactive_candlestick.html")

# 2. 技術指標圖
print("\n📈 生成技術指標圖...")
fig2 = create_technical_chart(
    df.tail(60),
    rsi=df['rsi'].tail(60),
    macd=df[['macd', 'signal', 'histogram']].tail(60),
    title="台積電 (2330) 技術指標"
)
fig2.write_html("interactive_indicators.html")
print("✅ 儲存至 interactive_indicators.html")

# 3. 回測結果圖
print("\n🔄 執行回測...")
engine = BacktestEngine(initial_capital=1000000)
strategy = sma_crossover_strategy(5, 20)
result = engine.run(df, strategy)

print(f"報酬率: {result['total_return_pct']:.2f}%")
print(f"交易次數: {result['total_trades']}")

print("\n📊 生成回測結果圖...")
fig3 = create_backtest_chart(
    result['equity_curve'],
    result['trades'],
    title="台積電 (2330) 回測結果 - MA5xMA20"
)
fig3.write_html("interactive_backtest.html")
print("✅ 儲存至 interactive_backtest.html")

print("\n\n" + "=" * 60)
print("✅ 互動式圖表生成完成!")
print("=" * 60)
print("\n📁 生成檔案:")
print("   - interactive_candlestick.html   K 線圖 + 均線")
print("   - interactive_indicators.html    技術指標 (RSI/MACD)")
print("   - interactive_backtest.html      回測結果")
print("\n💡 使用瀏覽器開啟 HTML 檔案即可互動操作!")
