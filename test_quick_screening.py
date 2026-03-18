#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速測試選股功能"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import pandas as pd
from datetime import datetime
from src.screener.strategies import screen_rsi_oversold, screen_golden_cross
from src.screener.advanced_strategies import screen_multi_factor

print("=" * 80)
print("🔍 快速選股測試")
print("=" * 80)

# 小範圍股票池 (只測試 5 檔，減少 API 請求)
STOCK_POOL = ['2330', '2454', '2317', '2412', '2308']

print(f"\n📅 日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"🎯 股票池: {len(STOCK_POOL)} 檔")
print()

results = {}

# === 策略 1: RSI 超賣 ===
print("-" * 80)
print("策略 1️⃣: RSI 超賣選股")
print("-" * 80)

try:
    rsi_result = screen_rsi_oversold(STOCK_POOL, rsi_threshold=35)
    if not rsi_result.empty:
        print(f"✅ 找到 {len(rsi_result)} 檔:")
        print(rsi_result[['stock_id', 'rsi', 'close']].to_string(index=False))
        results['RSI 超賣'] = rsi_result
    else:
        print("⚠️ 目前無超賣股票")
        results['RSI 超賣'] = None
except Exception as e:
    print(f"❌ 錯誤: {e}")
    results['RSI 超賣'] = None

print()

# === 策略 2: 黃金交叉 ===
print("-" * 80)
print("策略 2️⃣: 黃金交叉選股")
print("-" * 80)

try:
    golden_result = screen_golden_cross(STOCK_POOL)
    if not golden_result.empty:
        print(f"✅ 找到 {len(golden_result)} 檔:")
        print(golden_result[['stock_id', 'ma5', 'ma20', 'status']].to_string(index=False))
        results['黃金交叉'] = golden_result
    else:
        print("⚠️ 目前無黃金交叉")
        results['黃金交叉'] = None
except Exception as e:
    print(f"❌ 錯誤: {e}")
    results['黃金交叉'] = None

print()

# === 策略 3: 多因子評分 ===
print("-" * 80)
print("策略 3️⃣: 多因子評分 (>60 分)")
print("-" * 80)

try:
    multi_result = screen_multi_factor(STOCK_POOL, min_score=60)
    if not multi_result.empty:
        multi_result = multi_result.sort_values('total_score', ascending=False)
        print(f"✅ 找到 {len(multi_result)} 檔:")
        print(multi_result[['stock_id', 'total_score', 'close']].to_string(index=False))
        results['多因子評分'] = multi_result
    else:
        print("⚠️ 目前無高分股票")
        results['多因子評分'] = None
except Exception as e:
    print(f"❌ 錯誤: {e}")
    results['多因子評分'] = None

print()

# === 重點推薦 ===
print("=" * 80)
print("⭐️ 重點推薦 (出現在多個策略)")
print("=" * 80)

# 收集所有股票
all_stocks = set()
stock_count = {}

for strategy, df in results.items():
    if df is not None and not df.empty:
        stocks = set(df['stock_id'].tolist())
        for stock in stocks:
            stock_count[stock] = stock_count.get(stock, 0) + 1
        all_stocks.update(stocks)

# 找出出現在 2 個以上策略的股票
hot_stocks = {stock: count for stock, count in stock_count.items() if count >= 2}

if hot_stocks:
    hot_df = pd.DataFrame([
        {'股票代號': stock, '出現次數': count}
        for stock, count in sorted(hot_stocks.items(), key=lambda x: x[1], reverse=True)
    ])
    print(f"✅ 找到 {len(hot_stocks)} 檔重點股票:")
    print(hot_df.to_string(index=False))
else:
    print("⚠️ 目前無股票同時符合多個策略")

print()
print("=" * 80)
print("✅ 測試完成！")
print("=" * 80)
