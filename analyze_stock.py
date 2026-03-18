#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""股票技術分析工具"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime
from src.data.fetcher import TWSEFetcher
from src.indicators.technical import (
    calculate_ma, calculate_rsi, calculate_macd, 
    calculate_kd, calculate_bollinger_bands
)
from src.indicators.advanced import calculate_atr, calculate_obv

def analyze_stock(stock_id):
    """完整技術分析"""
    
    print("=" * 80)
    print(f"📊 {stock_id} 技術分析報告")
    print("=" * 80)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 抓取資料
    fetcher = TWSEFetcher()
    print("📥 抓取資料中...")
    df = fetcher.get_historical_price(stock_id, months=3)
    
    if df.empty:
        print("❌ 無法取得資料")
        return
    
    print(f"✅ 取得 {len(df)} 筆資料\n")
    
    # 計算指標
    df['ma5'] = calculate_ma(df['close'], 5)
    df['ma20'] = calculate_ma(df['close'], 20)
    df['ma60'] = calculate_ma(df['close'], 60)
    df['rsi'] = calculate_rsi(df['close'], 14)
    
    macd = calculate_macd(df['close'])
    df['macd'] = macd['macd']
    df['signal'] = macd['signal']
    df['histogram'] = macd['histogram']
    
    kd = calculate_kd(df['high'], df['low'], df['close'])
    df['k'] = kd['k']
    df['d'] = kd['d']
    
    bb = calculate_bollinger_bands(df['close'], 20, 2)
    df['bb_upper'] = bb['upper']
    df['bb_lower'] = bb['lower']
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 價格資訊
    print("=" * 80)
    print("📈 最新價格")
    print("=" * 80)
    print(f"日期: {latest['date']}")
    print(f"收盤: {latest['close']:.2f} 元")
    print(f"開盤: {latest['open']:.2f} 元")
    print(f"最高: {latest['high']:.2f} 元")
    print(f"最低: {latest['low']:.2f} 元")
    print(f"成交量: {latest['volume']:,.0f} 張")
    
    change = latest['close'] - prev['close']
    change_pct = (change / prev['close']) * 100
    emoji = "🟢" if change > 0 else "🔴"
    print(f"{emoji} 漲跌: {change:+.2f} 元 ({change_pct:+.2f}%)\n")
    
    # 技術指標
    print("=" * 80)
    print("📊 技術指標")
    print("=" * 80)
    
    # 1. MA
    print("\n【移動平均線】")
    print(f"MA5:  {latest['ma5']:.2f}")
    print(f"MA20: {latest['ma20']:.2f}")
    print(f"MA60: {latest['ma60']:.2f}")
    
    if latest['close'] > latest['ma5'] > latest['ma20']:
        ma_signal = "✅ 多頭排列"
    elif latest['close'] < latest['ma5'] < latest['ma20']:
        ma_signal = "❌ 空頭排列"
    elif latest['close'] > latest['ma20']:
        ma_signal = "🟢 中線多頭"
    else:
        ma_signal = "🔴 中線空頭"
    
    print(f"結論: {ma_signal}")
    
    # 2. RSI
    print("\n【RSI】")
    print(f"RSI(14): {latest['rsi']:.2f}")
    
    if latest['rsi'] > 70:
        rsi_signal = "🔴 超買"
    elif latest['rsi'] > 50:
        rsi_signal = "🟢 強勢"
    elif latest['rsi'] > 30:
        rsi_signal = "🟡 中性"
    else:
        rsi_signal = "✅ 超賣"
    
    print(f"結論: {rsi_signal}")
    
    # 3. MACD
    print("\n【MACD】")
    print(f"DIF:    {latest['macd']:.2f}")
    print(f"Signal: {latest['signal']:.2f}")
    print(f"柱狀圖: {latest['histogram']:.2f}")
    
    if latest['histogram'] > 0:
        macd_signal = "✅ 多頭" if latest['histogram'] > prev['histogram'] else "🟡 多頭減弱"
    else:
        macd_signal = "❌ 空頭" if latest['histogram'] < prev['histogram'] else "🟡 空頭減弱"
    
    print(f"結論: {macd_signal}")
    
    # 4. KD
    print("\n【KD】")
    print(f"K: {latest['k']:.2f}")
    print(f"D: {latest['d']:.2f}")
    
    if latest['k'] > 80:
        kd_signal = "🔴 超買"
    elif latest['k'] < 20:
        kd_signal = "✅ 超賣"
    elif latest['k'] > latest['d']:
        kd_signal = "🟢 多頭"
    else:
        kd_signal = "🔴 空頭"
    
    print(f"結論: {kd_signal}")
    
    # 5. 布林通道
    print("\n【布林通道】")
    print(f"上軌: {latest['bb_upper']:.2f}")
    print(f"下軌: {latest['bb_lower']:.2f}")
    print(f"現價: {latest['close']:.2f}")
    
    bb_pos = (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower']) * 100
    print(f"位置: {bb_pos:.1f}%")
    
    # 綜合評分
    print("\n" + "=" * 80)
    print("🎯 綜合評分")
    print("=" * 80)
    
    score = 0
    
    if latest['close'] > latest['ma5'] > latest['ma20']:
        score += 3
    elif latest['close'] > latest['ma20']:
        score += 1
    elif latest['close'] < latest['ma5'] < latest['ma20']:
        score -= 3
    
    if 30 < latest['rsi'] < 50:
        score += 2
    elif latest['rsi'] < 30:
        score += 3
    elif latest['rsi'] > 70:
        score -= 2
    
    if latest['histogram'] > 0 and latest['histogram'] > prev['histogram']:
        score += 3
    elif latest['histogram'] < 0 and latest['histogram'] < prev['histogram']:
        score -= 3
    
    if latest['k'] < 20:
        score += 2
    elif latest['k'] > 80:
        score -= 2
    
    print(f"\n總分: {score:+d} / 13")
    
    # 建議
    print("\n" + "=" * 80)
    print("💡 投資建議")
    print("=" * 80)
    
    if score >= 8:
        rec = "🟢 強烈買進"
    elif score >= 4:
        rec = "🟢 買進"
    elif score >= 1:
        rec = "🟡 偏多觀察"
    elif score >= -3:
        rec = "🟡 觀望"
    elif score >= -7:
        rec = "🔴 減碼"
    else:
        rec = "🔴 賣出"
    
    print(f"\n建議: {rec}")
    
    # 關鍵價位
    print("\n【關鍵價位】")
    recent = df.iloc[-20:]
    
    print(f"\n支撐:")
    print(f"  1. {latest['ma20']:.2f} 元 (月線)")
    print(f"  2. {latest['bb_lower']:.2f} 元 (下軌)")
    print(f"  3. {recent['low'].min():.2f} 元 (20日低)")
    
    print(f"\n壓力:")
    print(f"  1. {latest['ma5']:.2f} 元 (週線)")
    print(f"  2. {latest['bb_upper']:.2f} 元 (上軌)")
    print(f"  3. {recent['high'].max():.2f} 元 (20日高)")
    
    print("\n" + "=" * 80)
    print("✅ 分析完成")
    print("=" * 80)

if __name__ == "__main__":
    stock_id = sys.argv[1] if len(sys.argv) > 1 else '2330'
    analyze_stock(stock_id)
