"""完整示範程式"""
import sys
from src.screener.strategies import screen_rsi_oversold, screen_golden_cross, screen_momentum
from src.monitor.watcher import StockWatcher, console_alert_handler

# 測試用股票池 (台股權值股)
TEST_STOCKS = ['2330', '2317', '2454', '2412', '2308']  # 台積電、鴻海、聯發科、中華電、台達電


def demo_screener():
    """示範選股功能"""
    print("=" * 60)
    print("📊 台股分析器 - 選股功能示範")
    print("=" * 60)
    
    # 策略 1: RSI 超賣
    print("\n【策略 1】RSI 超賣 (RSI < 30)")
    print("-" * 60)
    result1 = screen_rsi_oversold(TEST_STOCKS, rsi_threshold=30)
    if not result1.empty:
        print("\n✅ 找到 RSI 超賣股票:")
        print(result1.to_string(index=False))
    else:
        print("\n❌ 無符合條件的股票")
    
    # 策略 2: 黃金交叉
    print("\n\n【策略 2】黃金交叉 (MA5 上穿 MA20)")
    print("-" * 60)
    result2 = screen_golden_cross(TEST_STOCKS)
    if not result2.empty:
        print("\n✅ 找到黃金交叉股票:")
        print(result2.to_string(index=False))
    else:
        print("\n❌ 無符合條件的股票")
    
    # 策略 3: 動能
    print("\n\n【策略 3】動能策略 (連續上漲 + 量增)")
    print("-" * 60)
    result3 = screen_momentum(TEST_STOCKS, min_volume=1000)
    if not result3.empty:
        print("\n✅ 找到動能強勁股票:")
        print(result3.to_string(index=False))
    else:
        print("\n❌ 無符合條件的股票")


def demo_monitor():
    """示範監控功能"""
    print("\n\n" + "=" * 60)
    print("📡 台股分析器 - 即時監控示範")
    print("=" * 60)
    
    # 建立監控器
    watcher = StockWatcher(check_interval=60)  # 每 60 秒檢查一次
    
    # 加入監控股票
    watcher.add_stock('2330', {
        'price_above': 2000,  # 股價突破 2000
        'rsi_below': 30       # RSI 跌破 30
    })
    
    watcher.add_stock('2454', {
        'price_below': 1000,  # 股價跌破 1000
        'volume_above': 50000 # 成交量超過 5 萬張
    })
    
    # 加入警報處理器
    watcher.add_alert_handler(console_alert_handler)
    
    # 執行一次檢查 (示範用)
    print("\n執行即時檢查...")
    alerts = watcher.check_once()
    
    if alerts:
        print(f"\n🚨 發現 {len(alerts)} 筆警報:")
        for stock_id, msgs in alerts.items():
            for msg in msgs:
                print(f"  • {stock_id}: {msg}")
    else:
        print("\n✅ 目前無警報")
    
    print("\n💡 提示: 實際使用時可呼叫 watcher.start_monitoring() 進行持續監控")


if __name__ == "__main__":
    try:
        # 1. 選股示範
        demo_screener()
        
        # 2. 監控示範
        demo_monitor()
        
        print("\n\n" + "=" * 60)
        print("✅ 示範完成!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 使用者中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
