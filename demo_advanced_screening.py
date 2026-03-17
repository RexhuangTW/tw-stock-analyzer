"""進階選股策略示範"""
from src.screener.advanced_strategies import (
    screen_breakout_with_volume,
    screen_bollinger_squeeze,
    screen_obv_divergence,
    screen_multi_factor
)

# 測試股票池 (擴大範圍)
STOCK_POOL = [
    '2330', '2317', '2454', '2412', '2308',  # 權值股
    '2303', '2382', '2881', '2882', '2891',  # 其他大型股
    '3711', '6505', '2357', '2379', '2395'   # 中型股
]

print("=" * 70)
print("🔍 進階選股策略示範")
print("=" * 70)
print(f"\n測試股票池: {len(STOCK_POOL)} 檔")

# 策略 1: 量價突破
print("\n\n【策略 1】量價突破策略")
print("-" * 70)
result1 = screen_breakout_with_volume(STOCK_POOL, lookback_days=20, volume_threshold=1.5)

if not result1.empty:
    print("\n✅ 找到量價突破標的:")
    print(result1[['stock_id', 'close', 'breakout_pct', 'volume_ratio']].to_string(index=False))
else:
    print("\n❌ 無符合條件的股票")

# 策略 2: 布林通道收縮
print("\n\n【策略 2】布林通道收縮策略")
print("-" * 70)
result2 = screen_bollinger_squeeze(STOCK_POOL, bb_period=20, squeeze_threshold=0.025)

if not result2.empty:
    print("\n✅ 找到布林收縮標的:")
    print(result2[['stock_id', 'close', 'bandwidth', 'position']].to_string(index=False))
else:
    print("\n❌ 無符合條件的股票")

# 策略 3: OBV 背離
print("\n\n【策略 3】OBV 背離策略")
print("-" * 70)
result3 = screen_obv_divergence(STOCK_POOL, lookback_days=30)

if not result3.empty:
    print("\n✅ 找到 OBV 背離標的:")
    print(result3[['stock_id', 'close', 'divergence', 'price_slope', 'obv_slope']].to_string(index=False))
else:
    print("\n❌ 無符合條件的股票")

# 策略 4: 多因子評分
print("\n\n【策略 4】多因子綜合評分")
print("-" * 70)
result4 = screen_multi_factor(STOCK_POOL[:10])  # 先測試 10 檔

if not result4.empty:
    print("\n✅ 多因子評分排行 (前 10 名):")
    print(result4.head(10)[['stock_id', 'total_score', 'trend_score', 'momentum_score', 'rsi', 'adx']].to_string(index=False))
else:
    print("\n❌ 無符合條件的股票")

print("\n\n" + "=" * 70)
print("✅ 進階選股策略示範完成!")
print("=" * 70)
