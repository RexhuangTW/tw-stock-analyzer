"""回測與視覺化示範"""
import sys
from src.data.fetcher import TWSEFetcher
from src.indicators.technical import calculate_ma, calculate_rsi, calculate_macd
from src.backtest.engine import BacktestEngine, sma_crossover_strategy, rsi_strategy
from src.visualization.charts import (
    plot_candlestick, 
    plot_technical_indicators, 
    plot_backtest_results
)
import matplotlib.pyplot as plt


def demo_visualization():
    """示範圖表視覺化"""
    print("=" * 60)
    print("📊 圖表視覺化示範")
    print("=" * 60)
    
    # 取得資料
    print("\n📡 抓取台積電 6 個月資料...")
    fetcher = TWSEFetcher()
    df = fetcher.get_historical_price("2330", months=6)
    
    print(f"✅ 取得 {len(df)} 筆資料")
    
    # 計算指標
    print("\n📈 計算技術指標...")
    df['ma5'] = calculate_ma(df['close'], 5)
    df['ma20'] = calculate_ma(df['close'], 20)
    df['ma60'] = calculate_ma(df['close'], 60)
    df['rsi'] = calculate_rsi(df['close'], 14)
    
    macd_df = calculate_macd(df['close'])
    df = df.join(macd_df)
    
    # 1. K線圖
    print("\n📊 繪製 K 線圖...")
    plot_candlestick(
        df.tail(60),  # 最近 60 天
        title="台積電 (2330) K線圖 - 近 60 日",
        save_path="output_candlestick.png",
        show_volume=True
    )
    
    # 2. 技術指標圖
    print("\n📈 繪製技術指標圖...")
    plot_technical_indicators(
        df.tail(60),
        indicators=['ma5', 'ma20', 'ma60', 'rsi', 'macd'],
        title="台積電 (2330) 技術指標 - 近 60 日",
        save_path="output_indicators.png"
    )
    
    print("\n✅ 圖表生成完成!")
    print("   - output_candlestick.png")
    print("   - output_indicators.png")


def demo_backtest():
    """示範回測功能"""
    print("\n\n" + "=" * 60)
    print("🔄 回測引擎示範")
    print("=" * 60)
    
    # 取得資料
    print("\n📡 抓取台積電 6 個月資料...")
    fetcher = TWSEFetcher()
    df = fetcher.get_historical_price("2330", months=6)
    
    print(f"✅ 取得 {len(df)} 筆資料 ({df['date'].min()} ~ {df['date'].max()})")
    
    # 策略 1: 均線交叉
    print("\n" + "-" * 60)
    print("【策略 1】均線交叉策略 (MA5 x MA20)")
    print("-" * 60)
    
    engine1 = BacktestEngine(initial_capital=1000000)
    strategy1 = sma_crossover_strategy(short_period=5, long_period=20)
    result1 = engine1.run(df, strategy1)
    
    print(f"\n初始資金: {result1['initial_capital']:,.0f} 元")
    print(f"最終淨值: {result1['final_equity']:,.0f} 元")
    print(f"總報酬率: {result1['total_return_pct']:.2f}%")
    print(f"最大回撤: {result1['max_drawdown_pct']:.2f}%")
    print(f"交易次數: {result1['total_trades']} 次")
    print(f"勝率: {result1['win_rate_pct']:.1f}%")
    
    # 繪製回測結果
    print("\n📊 繪製回測結果圖表...")
    plot_backtest_results(
        result1['equity_curve'],
        result1['trades'],
        title="台積電 (2330) 回測結果 - 均線交叉策略",
        save_path="output_backtest_sma.png"
    )
    
    # 策略 2: RSI
    print("\n" + "-" * 60)
    print("【策略 2】RSI 策略 (超賣買入/超買賣出)")
    print("-" * 60)
    
    engine2 = BacktestEngine(initial_capital=1000000)
    strategy2 = rsi_strategy(period=14, oversold=30, overbought=70)
    result2 = engine2.run(df, strategy2)
    
    print(f"\n初始資金: {result2['initial_capital']:,.0f} 元")
    print(f"最終淨值: {result2['final_equity']:,.0f} 元")
    print(f"總報酬率: {result2['total_return_pct']:.2f}%")
    print(f"最大回撤: {result2['max_drawdown_pct']:.2f}%")
    print(f"交易次數: {result2['total_trades']} 次")
    print(f"勝率: {result2['win_rate_pct']:.1f}%")
    
    # 繪製回測結果
    print("\n📊 繪製回測結果圖表...")
    plot_backtest_results(
        result2['equity_curve'],
        result2['trades'],
        title="台積電 (2330) 回測結果 - RSI 策略",
        save_path="output_backtest_rsi.png"
    )
    
    # 比較
    print("\n" + "=" * 60)
    print("📊 策略比較")
    print("=" * 60)
    print(f"\n{'策略':<20} {'報酬率':<12} {'最大回撤':<12} {'勝率':<10} {'交易次數'}")
    print("-" * 60)
    print(f"{'均線交叉 (MA5xMA20)':<20} {result1['total_return_pct']:>10.2f}% "
          f"{result1['max_drawdown_pct']:>10.2f}% {result1['win_rate_pct']:>8.1f}% "
          f"{result1['total_trades']:>8}")
    print(f"{'RSI (30/70)':<20} {result2['total_return_pct']:>10.2f}% "
          f"{result2['max_drawdown_pct']:>10.2f}% {result2['win_rate_pct']:>8.1f}% "
          f"{result2['total_trades']:>8}")
    
    print("\n✅ 回測圖表生成完成!")
    print("   - output_backtest_sma.png")
    print("   - output_backtest_rsi.png")


if __name__ == "__main__":
    try:
        # 1. 視覺化示範
        demo_visualization()
        
        # 2. 回測示範
        demo_backtest()
        
        print("\n\n" + "=" * 60)
        print("✅ 所有示範完成!")
        print("=" * 60)
        print("\n📁 生成檔案:")
        print("   - output_candlestick.png       K線圖")
        print("   - output_indicators.png        技術指標圖")
        print("   - output_backtest_sma.png      均線交叉回測")
        print("   - output_backtest_rsi.png      RSI 策略回測")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 使用者中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
