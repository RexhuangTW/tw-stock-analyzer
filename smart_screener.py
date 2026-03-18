#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能選股器 - 基於回測績效的加權選股系統"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import json
import time
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from src.data.fetcher import TWSEFetcher
from src.indicators.technical import calculate_ma, calculate_rsi, calculate_macd, calculate_bollinger_bands
from strategy_backtest import STRATEGIES, prepare_data, load_strategy_state, STRATEGY_STATE_FILE

PICK_HISTORY_FILE = Path(__file__).parent / "pick_history.json"


def load_pick_history():
    if PICK_HISTORY_FILE.exists():
        with open(PICK_HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {'picks': []}


def save_pick_history(history):
    with open(PICK_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2, ensure_ascii=False, default=str)


def get_strategy_weights():
    """從回測結果取得策略權重"""
    state = load_strategy_state()
    if state and 'strategy_weights' in state:
        return state['strategy_weights']
    
    # 預設等權重
    return {name: 1.0 / len(STRATEGIES) for name in STRATEGIES}


def score_stock(df, weights):
    """用回測驗證過的權重對股票評分"""
    if len(df) < 30:
        return None
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    signals = {}
    
    # RSI 超賣
    if latest['rsi'] < 30:
        signals['rsi_oversold'] = 3
    elif latest['rsi'] < 40:
        signals['rsi_oversold'] = 1
    else:
        signals['rsi_oversold'] = -1
    
    # 黃金交叉
    if prev['ma5'] <= prev['ma20'] and latest['ma5'] > latest['ma20']:
        signals['golden_cross'] = 3
    elif latest['ma5'] > latest['ma20']:
        signals['golden_cross'] = 1
    elif latest['ma5'] < latest['ma20']:
        signals['golden_cross'] = -2
    else:
        signals['golden_cross'] = 0
    
    # MACD 交叉
    if latest['macd_hist'] > 0 and latest['macd_hist'] > prev['macd_hist']:
        signals['macd_cross'] = 3
    elif latest['macd_hist'] > 0:
        signals['macd_cross'] = 1
    elif latest['macd_hist'] < 0:
        signals['macd_cross'] = -2
    else:
        signals['macd_cross'] = 0
    
    # 布林下軌
    if latest['close'] <= latest['bb_lower']:
        signals['bollinger_lower'] = 3
    elif latest['close'] >= latest['bb_upper']:
        signals['bollinger_lower'] = -2
    else:
        bb_pos = (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])
        signals['bollinger_lower'] = 1 if bb_pos < 0.3 else 0
    
    # 多頭排列
    if latest['close'] > latest['ma5'] > latest['ma20']:
        signals['multi_trend'] = 3
    elif latest['close'] > latest['ma20']:
        signals['multi_trend'] = 1
    elif latest['close'] < latest['ma5'] < latest['ma20']:
        signals['multi_trend'] = -3
    else:
        signals['multi_trend'] = 0
    
    # 綜合評分 (用回測權重加權)
    total_score = 0
    for strat_name, signal_score in signals.items():
        w = weights.get(strat_name, 0.1)
        total_score += signal_score * w
    
    # Normalize to 0-100
    max_possible = 3 * sum(weights.values())
    min_possible = -3 * sum(weights.values())
    normalized = (total_score - min_possible) / (max_possible - min_possible) * 100
    
    return {
        'raw_score': round(total_score, 2),
        'normalized_score': round(normalized, 1),
        'signals': signals,
        'rsi': round(latest['rsi'], 1),
        'ma_trend': '多頭' if latest['close'] > latest['ma5'] > latest['ma20'] else 
                    '空頭' if latest['close'] < latest['ma5'] < latest['ma20'] else '盤整',
        'close': latest['close'],
        'macd_hist': round(latest['macd_hist'], 2),
    }


def smart_screen(stock_ids=None):
    """智能選股"""
    
    if stock_ids is None:
        stock_ids = [
            '2330','2317','2454','2308','2412','2881','2882','2886','2891',
            '8046','2486','3189','3037','2337','2344','2603','1301','2002',
            '2303','2357','2382','3008','5880','2474','2912','6505',
            '3443','6669','4919','6415','2345','3231','1216','2327'
        ]
    
    weights = get_strategy_weights()
    state = load_strategy_state()
    
    print("=" * 80)
    print("智能選股系統 (回測驗證版)")
    print("=" * 80)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"股票池: {len(stock_ids)} 檔")
    
    if state:
        print(f"策略狀態: {state['last_updated']}")
        print(f"\n策略權重 (依回測績效):")
        for name, w in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            strat_name = STRATEGIES.get(name, {}).get('name', name)
            perf = state['strategies'].get(name, {}).get('performance', {})
            wr = perf.get('win_rate', '?')
            print(f"  {strat_name:12s}: 權重 {w:.1%}, 勝率 {wr}%")
    else:
        print("策略狀態: 未回測 (使用等權重)")
        print("建議先執行: python3 strategy_backtest.py")
    
    print()
    
    fetcher = TWSEFetcher()
    results = []
    
    for sid in stock_ids:
        try:
            df = fetcher.get_historical_price(sid, months=3)
            if df.empty or len(df) < 30:
                continue
            
            df = prepare_data(df)
            score_data = score_stock(df, weights)
            
            if score_data:
                score_data['stock_id'] = sid
                results.append(score_data)
            
            time.sleep(0.5)
        except:
            continue
    
    # 排序
    results.sort(key=lambda x: x['normalized_score'], reverse=True)
    
    # 輸出
    print(f"\n{'=' * 80}")
    print(f"選股結果 (共 {len(results)} 檔)")
    print(f"{'=' * 80}")
    
    # 買進候選
    buys = [r for r in results if r['normalized_score'] >= 65]
    watches = [r for r in results if 50 <= r['normalized_score'] < 65]
    avoids = [r for r in results if r['normalized_score'] < 40]
    
    print(f"\n--- 買進候選 (>= 65分) ---\n")
    if buys:
        print(f"{'股票':6s} {'收盤':>8s} {'評分':>6s} {'RSI':>6s} {'均線':>6s} {'MACD柱':>8s}")
        print("-" * 50)
        for r in buys:
            print(f"{r['stock_id']:6s} {r['close']:8.1f} {r['normalized_score']:6.1f} {r['rsi']:6.1f} {r['ma_trend']:>6s} {r['macd_hist']:+8.2f}")
    else:
        print("無")
    
    print(f"\n--- 觀察名單 (50-65分) ---\n")
    if watches:
        print(f"{'股票':6s} {'收盤':>8s} {'評分':>6s} {'RSI':>6s} {'均線':>6s}")
        print("-" * 40)
        for r in watches[:10]:
            print(f"{r['stock_id']:6s} {r['close']:8.1f} {r['normalized_score']:6.1f} {r['rsi']:6.1f} {r['ma_trend']:>6s}")
    else:
        print("無")
    
    print(f"\n--- 避開名單 (< 40分) ---\n")
    if avoids:
        for r in avoids:
            print(f"  {r['stock_id']}: {r['normalized_score']}分 ({r['ma_trend']})")
    else:
        print("無")
    
    # 儲存選股紀錄
    today = datetime.now().strftime('%Y-%m-%d')
    history = load_pick_history()
    
    pick_record = {
        'date': today,
        'buys': [{'stock_id': r['stock_id'], 'score': r['normalized_score'], 'close': r['close']} for r in buys],
        'watches': [{'stock_id': r['stock_id'], 'score': r['normalized_score'], 'close': r['close']} for r in watches[:5]],
    }
    
    # 移除今天舊的紀錄
    history['picks'] = [p for p in history['picks'] if p['date'] != today]
    history['picks'].append(pick_record)
    
    # 只保留 60 天
    cutoff = (datetime.now() - pd.Timedelta(days=60)).strftime('%Y-%m-%d')
    history['picks'] = [p for p in history['picks'] if p['date'] >= cutoff]
    
    save_pick_history(history)
    
    print(f"\n選股紀錄已儲存: {PICK_HISTORY_FILE}")
    print(f"{'=' * 80}")
    
    return results


def track_performance():
    """追蹤過去選股的實際表現"""
    history = load_pick_history()
    fetcher = TWSEFetcher()
    
    print("=" * 80)
    print("選股績效追蹤")
    print("=" * 80)
    
    results = []
    
    for pick in history.get('picks', []):
        pick_date = pick['date']
        
        for stock in pick.get('buys', []):
            sid = stock['stock_id']
            entry_price = stock['close']
            
            try:
                df = fetcher.get_historical_price(sid, months=2)
                if df.empty:
                    continue
                
                # 找到選股日之後的價格
                df['date_str'] = df['date'].astype(str).str[:10]
                after = df[df['date_str'] > pick_date]
                
                if len(after) >= 1:
                    # 1天後、3天後、5天後報酬
                    d1 = after.iloc[0]['close'] if len(after) >= 1 else None
                    d3 = after.iloc[2]['close'] if len(after) >= 3 else None
                    d5 = after.iloc[4]['close'] if len(after) >= 5 else None
                    
                    results.append({
                        'date': pick_date,
                        'stock_id': sid,
                        'entry': entry_price,
                        'score': stock['score'],
                        'd1_return': round((d1 - entry_price) / entry_price * 100, 2) if d1 else None,
                        'd3_return': round((d3 - entry_price) / entry_price * 100, 2) if d3 else None,
                        'd5_return': round((d5 - entry_price) / entry_price * 100, 2) if d5 else None,
                    })
                
                time.sleep(0.5)
            except:
                continue
    
    if results:
        df_results = pd.DataFrame(results)
        
        print(f"\n追蹤紀錄: {len(results)} 筆\n")
        
        for col in ['d1_return', 'd3_return', 'd5_return']:
            valid = df_results[col].dropna()
            if len(valid) > 0:
                days = col.split('_')[0][1:]
                wins = (valid > 0).sum()
                print(f"{days}天後: 勝率 {wins/len(valid)*100:.1f}%, 平均報酬 {valid.mean():+.2f}%")
        
        print(f"\n明細:")
        print(df_results[['date','stock_id','entry','score','d1_return','d3_return','d5_return']].to_string(index=False))
    else:
        print("尚無追蹤紀錄")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'track':
        track_performance()
    else:
        smart_screen()
