#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🔍 每日選股工具 - 自動找出適合買入的股票"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import pandas as pd
from datetime import datetime
from src.screener.strategies import screen_rsi_oversold, screen_golden_cross, screen_momentum
from src.screener.advanced_strategies import (
    screen_breakout_with_volume, 
    screen_bollinger_squeeze, 
    screen_multi_factor
)

# ==================== 設定 ====================

# 台灣 50 成分股 (可自行調整)
STOCK_POOL = [
    '2330', '2317', '2454', '2412', '2308',  # 科技股
    '2882', '2881', '2886', '2891', '2892',  # 金融股
    '2303', '2002', '1301', '1303', '2207',  # 傳產
    '2357', '2382', '3008', '3711', '5880',  # 其他
    '2408', '2409', '3045', '2327', '2345',
    '6505', '2395', '3231', '1216', '2474'
]

# 參數設定
RSI_THRESHOLD = 35          # RSI 低於此值視為超賣
MULTI_FACTOR_MIN = 60       # 多因子最低分數
LOOKBACK_DAYS = 20          # 量價突破回溯天數
SQUEEZE_THRESHOLD = 0.05    # 布林通道收縮閾值

# ==================== 主程式 ====================

def print_separator(title="", char="=", width=80):
    """印出分隔線"""
    if title:
        print(f"\n{char * width}")
        print(f"{title:^{width}}")
        print(f"{char * width}")
    else:
        print(f"{char * width}")

def format_result(df, columns, title):
    """格式化輸出結果"""
    if df.empty:
        print(f"⚠️  {title}: 目前無符合條件股票\n")
        return None
    
    print(f"✅ {title}: 找到 {len(df)} 檔")
    print(df[columns].to_string(index=False))
    print()
    return df

def save_to_markdown(results_dict, date_str):
    """儲存結果到 Markdown 檔案"""
    output_dir = Path("screening_results")
    output_dir.mkdir(exist_ok=True)
    
    filename = output_dir / f"screening_{date_str}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# 📊 台股選股結果 - {date_str}\n\n")
        f.write(f"**執行時間:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        for strategy, result in results_dict.items():
            f.write(f"## {strategy}\n\n")
            if result is not None and not result.empty:
                f.write(result.to_markdown(index=False))
                f.write("\n\n")
            else:
                f.write("⚠️ 目前無符合條件股票\n\n")
        
        f.write("---\n\n")
        f.write("**使用說明:**\n")
        f.write("- ⭐️ 重點關注: 同時出現在多個策略的股票\n")
        f.write("- 📈 建議搭配 K 線圖確認進場點\n")
        f.write("- ⚠️ 記得設定停損停利\n")
    
    print(f"📄 結果已儲存: {filename}\n")
    return filename

def main():
    """主程式"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    print_separator("🔍 台股每日選股工具", "=", 80)
    print(f"📅 日期: {date_str}")
    print(f"🎯 股票池: {len(STOCK_POOL)} 檔")
    print()
    
    results = {}
    
    # ==================== 策略 1: RSI 超賣 ====================
    print_separator("策略 1️⃣: RSI 超賣選股 (逢低買進)", "-", 80)
    print(f"條件: RSI < {RSI_THRESHOLD}")
    print("適合: 短線反彈交易\n")
    
    try:
        rsi_result = screen_rsi_oversold(STOCK_POOL, rsi_threshold=RSI_THRESHOLD)
        if not rsi_result.empty:
            rsi_result = rsi_result.sort_values('rsi')
            results['1️⃣ RSI 超賣 (短線反彈)'] = format_result(
                rsi_result, 
                ['stock_id', 'rsi', 'close'],
                "RSI 超賣股票"
            )
    except Exception as e:
        print(f"❌ 錯誤: {e}\n")
        results['1️⃣ RSI 超賣 (短線反彈)'] = None
    
    # ==================== 策略 2: 黃金交叉 ====================
    print_separator("策略 2️⃣: 黃金交叉選股 (趨勢轉多)", "-", 80)
    print("條件: MA5 向上突破 MA20")
    print("適合: 中線波段操作\n")
    
    try:
        golden_result = screen_golden_cross(STOCK_POOL)
        if not golden_result.empty:
            results['2️⃣ 黃金交叉 (趨勢轉多)'] = format_result(
                golden_result,
                ['stock_id', 'ma5', 'ma20', 'status'],
                "黃金交叉股票"
            )
    except Exception as e:
        print(f"❌ 錯誤: {e}\n")
        results['2️⃣ 黃金交叉 (趨勢轉多)'] = None
    
    # ==================== 策略 3: 動能策略 ====================
    print_separator("策略 3️⃣: 動能策略 (強勢追蹤)", "-", 80)
    print("條件: 連續上漲 + 量能放大")
    print("適合: 追強勢股\n")
    
    try:
        momentum_result = screen_momentum(STOCK_POOL, min_volume=2000)
        if not momentum_result.empty:
            results['3️⃣ 動能策略 (強勢股)'] = format_result(
                momentum_result,
                ['stock_id', 'consecutive_up', 'volume_ratio'],
                "動能強勢股"
            )
    except Exception as e:
        print(f"❌ 錯誤: {e}\n")
        results['3️⃣ 動能策略 (強勢股)'] = None
    
    # ==================== 策略 4: 量價突破 ====================
    print_separator("策略 4️⃣: 量價突破 (突破整理)", "-", 80)
    print(f"條件: 突破 {LOOKBACK_DAYS} 日高點 + 量增")
    print("適合: 突破買進\n")
    
    try:
        breakout_result = screen_breakout_with_volume(STOCK_POOL, lookback_days=LOOKBACK_DAYS)
        if not breakout_result.empty:
            results['4️⃣ 量價突破 (突破整理)'] = format_result(
                breakout_result,
                ['stock_id', 'breakout_pct', 'volume_ratio'],
                "量價突破股票"
            )
    except Exception as e:
        print(f"❌ 錯誤: {e}\n")
        results['4️⃣ 量價突破 (突破整理)'] = None
    
    # ==================== 策略 5: 布林收縮 ====================
    print_separator("策略 5️⃣: 布林通道收縮 (盤整待噴)", "-", 80)
    print(f"條件: 布林通道寬度 < {SQUEEZE_THRESHOLD}")
    print("適合: 提前卡位等噴出\n")
    
    try:
        squeeze_result = screen_bollinger_squeeze(STOCK_POOL, squeeze_threshold=SQUEEZE_THRESHOLD)
        if not squeeze_result.empty:
            results['5️⃣ 布林收縮 (盤整待噴)'] = format_result(
                squeeze_result,
                ['stock_id', 'bandwidth', 'close'],
                "布林收縮股票"
            )
    except Exception as e:
        print(f"❌ 錯誤: {e}\n")
        results['5️⃣ 布林收縮 (盤整待噴)'] = None
    
    # ==================== 策略 6: 多因子評分 ====================
    print_separator("策略 6️⃣: 多因子綜合評分 (全面評估)", "-", 80)
    print(f"條件: 綜合評分 > {MULTI_FACTOR_MIN} 分")
    print("適合: 穩健投資\n")
    
    try:
        multi_result = screen_multi_factor(STOCK_POOL, min_score=MULTI_FACTOR_MIN)
        if not multi_result.empty:
            multi_result = multi_result.sort_values('total_score', ascending=False)
            results['6️⃣ 多因子評分 (綜合評估)'] = format_result(
                multi_result.head(10),
                ['stock_id', 'total_score', 'close'],
                "高評分股票 (Top 10)"
            )
    except Exception as e:
        print(f"❌ 錯誤: {e}\n")
        results['6️⃣ 多因子評分 (綜合評估)'] = None
    
    # ==================== 重點推薦 ====================
    print_separator("⭐️ 重點推薦 (出現在多個策略)", "-", 80)
    
    # 收集所有有結果的股票
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
        print()
        results['⭐️ 重點推薦'] = hot_df
    else:
        print("⚠️ 目前無股票同時符合多個策略\n")
        results['⭐️ 重點推薦'] = None
    
    # ==================== 儲存結果 ====================
    filename = save_to_markdown(results, date_str)
    
    # ==================== 總結 ====================
    print_separator("📊 選股總結", "=", 80)
    total_picks = sum(1 for r in results.values() if r is not None and not r.empty)
    print(f"✅ 有結果策略: {total_picks}/6")
    print(f"⭐️ 重點股票: {len(hot_stocks) if hot_stocks else 0} 檔")
    print(f"📄 報告位置: {filename}")
    print()
    print("💡 建議:")
    print("  1. 優先關注「重點推薦」的股票")
    print("  2. 搭配 Streamlit 查看 K 線圖確認")
    print("  3. 記得設定停損停利點")
    print_separator("", "=", 80)

if __name__ == "__main__":
    main()
