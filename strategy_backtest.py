#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""策略回測與優化引擎 - 用歷史數據驗證每個策略的實際表現"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from src.data.fetcher import TWSEFetcher
from src.indicators.technical import calculate_ma, calculate_rsi, calculate_macd, calculate_kd, calculate_bollinger_bands

STRATEGY_STATE_FILE = Path(__file__).parent / "strategy_state.json"

# ==================== 策略定義 ====================

def strategy_rsi_oversold(df, i, params):
    """RSI 超賣策略"""
    threshold = params.get('rsi_threshold', 30)
    if i < 14:
        return None
    if df.iloc[i]['rsi'] < threshold:
        return 'BUY'
    return None

def strategy_rsi_oversold_exit(df, i, params):
    """RSI 超賣出場"""
    if df.iloc[i]['rsi'] > 60:
        return 'SELL'
    return None

def strategy_golden_cross(df, i, params):
    """黃金交叉策略"""
    if i < 20:
        return None
    if df.iloc[i-1]['ma5'] <= df.iloc[i-1]['ma20'] and df.iloc[i]['ma5'] > df.iloc[i]['ma20']:
        return 'BUY'
    return None

def strategy_golden_cross_exit(df, i, params):
    """死亡交叉出場"""
    if i < 20:
        return None
    if df.iloc[i-1]['ma5'] >= df.iloc[i-1]['ma20'] and df.iloc[i]['ma5'] < df.iloc[i]['ma20']:
        return 'SELL'
    return None

def strategy_macd_cross(df, i, params):
    """MACD 黃金交叉策略"""
    if i < 26:
        return None
    if df.iloc[i-1]['macd_hist'] <= 0 and df.iloc[i]['macd_hist'] > 0:
        return 'BUY'
    return None

def strategy_macd_cross_exit(df, i, params):
    """MACD 死亡交叉出場"""
    if i < 26:
        return None
    if df.iloc[i-1]['macd_hist'] >= 0 and df.iloc[i]['macd_hist'] < 0:
        return 'SELL'
    return None

def strategy_bollinger_lower(df, i, params):
    """布林通道下軌反彈策略"""
    if i < 20:
        return None
    if df.iloc[i]['close'] <= df.iloc[i]['bb_lower']:
        return 'BUY'
    return None

def strategy_bollinger_exit(df, i, params):
    """布林通道上軌出場"""
    if i < 20:
        return None
    if df.iloc[i]['close'] >= df.iloc[i]['bb_upper']:
        return 'SELL'
    return None

def strategy_multi_trend(df, i, params):
    """多頭排列策略"""
    if i < 20:
        return None
    row = df.iloc[i]
    prev = df.iloc[i-1]
    
    # 多頭排列形成
    if row['close'] > row['ma5'] > row['ma20']:
        if not (prev['close'] > prev['ma5'] > prev['ma20']):
            return 'BUY'
    return None

def strategy_multi_trend_exit(df, i, params):
    """多頭排列破壞出場"""
    if i < 20:
        return None
    if df.iloc[i]['close'] < df.iloc[i]['ma20']:
        return 'SELL'
    return None

def strategy_composite(df, i, params):
    """綜合評分策略 - 多指標共振"""
    if i < 26:
        return None
    
    row = df.iloc[i]
    prev = df.iloc[i-1]
    score = 0
    
    weights = params.get('weights', {
        'ma': 1.0, 'rsi': 1.0, 'macd': 1.0, 'bb': 1.0
    })
    
    # MA 訊號
    if row['close'] > row['ma5'] > row['ma20']:
        score += 2 * weights.get('ma', 1.0)
    elif row['close'] > row['ma20']:
        score += 1 * weights.get('ma', 1.0)
    elif row['close'] < row['ma5'] < row['ma20']:
        score -= 2 * weights.get('ma', 1.0)
    
    # RSI 訊號
    if row['rsi'] < 30:
        score += 2 * weights.get('rsi', 1.0)
    elif 30 <= row['rsi'] <= 50:
        score += 1 * weights.get('rsi', 1.0)
    elif row['rsi'] > 70:
        score -= 1 * weights.get('rsi', 1.0)
    
    # MACD 訊號
    if row['macd_hist'] > 0 and row['macd_hist'] > prev['macd_hist']:
        score += 2 * weights.get('macd', 1.0)
    elif row['macd_hist'] > 0:
        score += 1 * weights.get('macd', 1.0)
    elif row['macd_hist'] < 0:
        score -= 1 * weights.get('macd', 1.0)
    
    # 布林通道
    if row['close'] <= row['bb_lower']:
        score += 2 * weights.get('bb', 1.0)
    elif row['close'] >= row['bb_upper']:
        score -= 1 * weights.get('bb', 1.0)
    
    threshold = params.get('buy_threshold', 4.0)
    if score >= threshold:
        return 'BUY'
    return None

def strategy_composite_exit(df, i, params):
    """綜合評分出場"""
    if i < 26:
        return None
    row = df.iloc[i]
    prev = df.iloc[i-1]
    
    # 停利停損
    score = 0
    if row['close'] < row['ma5'] < row['ma20']:
        score -= 2
    if row['rsi'] > 70:
        score -= 1
    if row['macd_hist'] < 0 and row['macd_hist'] < prev['macd_hist']:
        score -= 2
    
    if score <= -3:
        return 'SELL'
    return None


# ==================== 回測引擎 ====================

STRATEGIES = {
    'rsi_oversold': {
        'name': 'RSI 超賣',
        'entry': strategy_rsi_oversold,
        'exit': strategy_rsi_oversold_exit,
        'default_params': {'rsi_threshold': 30},
        'param_ranges': {'rsi_threshold': [25, 30, 35, 40]},
    },
    'golden_cross': {
        'name': '黃金交叉',
        'entry': strategy_golden_cross,
        'exit': strategy_golden_cross_exit,
        'default_params': {},
        'param_ranges': {},
    },
    'macd_cross': {
        'name': 'MACD 交叉',
        'entry': strategy_macd_cross,
        'exit': strategy_macd_cross_exit,
        'default_params': {},
        'param_ranges': {},
    },
    'bollinger_lower': {
        'name': '布林下軌反彈',
        'entry': strategy_bollinger_lower,
        'exit': strategy_bollinger_exit,
        'default_params': {},
        'param_ranges': {},
    },
    'multi_trend': {
        'name': '多頭排列',
        'entry': strategy_multi_trend,
        'exit': strategy_multi_trend_exit,
        'default_params': {},
        'param_ranges': {},
    },
    'composite': {
        'name': '綜合評分',
        'entry': strategy_composite,
        'exit': strategy_composite_exit,
        'default_params': {
            'buy_threshold': 4.0,
            'weights': {'ma': 1.0, 'rsi': 1.0, 'macd': 1.0, 'bb': 1.0}
        },
        'param_ranges': {
            'buy_threshold': [3.0, 4.0, 5.0, 6.0],
        },
    },
}


def prepare_data(df):
    """計算所有技術指標"""
    df = df.copy()
    df['ma5'] = calculate_ma(df['close'], 5)
    df['ma10'] = calculate_ma(df['close'], 10)
    df['ma20'] = calculate_ma(df['close'], 20)
    df['rsi'] = calculate_rsi(df['close'], 14)
    
    macd = calculate_macd(df['close'])
    df['macd_line'] = macd['macd']
    df['macd_signal'] = macd['signal']
    df['macd_hist'] = macd['histogram']
    
    bb = calculate_bollinger_bands(df['close'], 20, 2)
    df['bb_upper'] = bb['upper']
    df['bb_lower'] = bb['lower']
    
    return df


def backtest_strategy(df, strategy_name, params=None, fee_rate=0.001425, tax_rate=0.003, max_hold_days=20):
    """回測單一策略"""
    strategy = STRATEGIES[strategy_name]
    if params is None:
        params = strategy['default_params']
    
    entry_fn = strategy['entry']
    exit_fn = strategy['exit']
    
    trades = []
    position = None  # {'date': ..., 'price': ..., 'index': ...}
    
    for i in range(1, len(df)):
        if position is None:
            # 尋找進場點
            signal = entry_fn(df, i, params)
            if signal == 'BUY':
                position = {
                    'entry_date': df.iloc[i]['date'],
                    'entry_price': df.iloc[i]['close'],
                    'entry_index': i
                }
        else:
            # 檢查出場
            hold_days = i - position['entry_index']
            exit_signal = exit_fn(df, i, params)
            
            # 出場條件: 策略訊號 或 超過最大持有天數 或 停損 -7%
            stop_loss = df.iloc[i]['close'] < position['entry_price'] * 0.93
            
            if exit_signal == 'SELL' or hold_days >= max_hold_days or stop_loss:
                exit_price = df.iloc[i]['close']
                entry_price = position['entry_price']
                
                # 計算報酬 (含手續費和證交稅)
                buy_cost = entry_price * (1 + fee_rate)
                sell_revenue = exit_price * (1 - fee_rate - tax_rate)
                return_pct = (sell_revenue - buy_cost) / buy_cost * 100
                
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': df.iloc[i]['date'],
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'hold_days': hold_days,
                    'return_pct': return_pct,
                    'exit_reason': 'signal' if exit_signal else ('stop_loss' if stop_loss else 'max_hold'),
                })
                position = None
    
    return trades


def evaluate_trades(trades):
    """評估交易績效"""
    if not trades:
        return {
            'total_trades': 0,
            'win_rate': 0,
            'avg_return': 0,
            'max_return': 0,
            'min_return': 0,
            'avg_hold_days': 0,
            'total_return': 0,
            'profit_factor': 0,
            'score': 0,
        }
    
    returns = [t['return_pct'] for t in trades]
    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r <= 0]
    
    win_rate = len(wins) / len(returns) * 100 if returns else 0
    avg_return = np.mean(returns) if returns else 0
    total_return = np.sum(returns)
    avg_hold = np.mean([t['hold_days'] for t in trades])
    
    gross_profit = sum(wins) if wins else 0
    gross_loss = abs(sum(losses)) if losses else 0.01
    profit_factor = gross_profit / gross_loss
    
    # 綜合評分: 勝率 * 平均報酬 * profit_factor
    score = (win_rate / 100) * avg_return * min(profit_factor, 3.0)
    
    return {
        'total_trades': len(trades),
        'win_rate': round(win_rate, 1),
        'avg_return': round(avg_return, 2),
        'max_return': round(max(returns), 2) if returns else 0,
        'min_return': round(min(returns), 2) if returns else 0,
        'avg_hold_days': round(avg_hold, 1),
        'total_return': round(total_return, 2),
        'profit_factor': round(profit_factor, 2),
        'score': round(score, 2),
    }


# ==================== 主程式 ====================

def run_full_backtest(stock_ids=None):
    """對所有策略進行完整回測"""
    
    if stock_ids is None:
        stock_ids = ['2330', '2317', '2454', '2308', '2412', '2881', '2886',
                     '8046', '3189', '3037', '2337', '2344', '2603', '1301']
    
    fetcher = TWSEFetcher()
    all_results = {}
    
    print("=" * 80)
    print("策略回測引擎")
    print("=" * 80)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"股票數: {len(stock_ids)}")
    print(f"策略數: {len(STRATEGIES)}")
    print()
    
    # 收集所有股票的歷史資料
    stock_data = {}
    for sid in stock_ids:
        try:
            df = fetcher.get_historical_price(sid, months=6)
            if not df.empty and len(df) >= 30:
                df = prepare_data(df)
                stock_data[sid] = df
                print(f"  {sid}: {len(df)} 筆資料")
        except Exception as e:
            print(f"  {sid}: 失敗 ({e})")
        import time
        time.sleep(0.5)
    
    print(f"\n成功載入 {len(stock_data)} 檔股票資料\n")
    
    # 對每個策略進行回測
    for strat_name, strat_info in STRATEGIES.items():
        print(f"\n{'=' * 80}")
        print(f"策略: {strat_info['name']} ({strat_name})")
        print(f"{'=' * 80}")
        
        all_trades = []
        
        for sid, df in stock_data.items():
            trades = backtest_strategy(df, strat_name)
            for t in trades:
                t['stock_id'] = sid
            all_trades.extend(trades)
        
        perf = evaluate_trades(all_trades)
        all_results[strat_name] = {
            'performance': perf,
            'params': strat_info['default_params'],
            'trades': all_trades,
        }
        
        print(f"  交易次數: {perf['total_trades']}")
        print(f"  勝率: {perf['win_rate']}%")
        print(f"  平均報酬: {perf['avg_return']}%")
        print(f"  最大獲利: {perf['max_return']}%")
        print(f"  最大虧損: {perf['min_return']}%")
        print(f"  平均持有: {perf['avg_hold_days']} 天")
        print(f"  Profit Factor: {perf['profit_factor']}")
        print(f"  綜合評分: {perf['score']}")
        
        # 參數優化
        if strat_info.get('param_ranges'):
            print(f"\n  --- 參數優化 ---")
            best_score = perf['score']
            best_params = strat_info['default_params'].copy()
            
            for param_name, param_values in strat_info['param_ranges'].items():
                for val in param_values:
                    test_params = strat_info['default_params'].copy()
                    test_params[param_name] = val
                    
                    test_trades = []
                    for sid, df in stock_data.items():
                        trades = backtest_strategy(df, strat_name, test_params)
                        test_trades.extend(trades)
                    
                    test_perf = evaluate_trades(test_trades)
                    print(f"  {param_name}={val}: 勝率={test_perf['win_rate']}% 報酬={test_perf['avg_return']}% 評分={test_perf['score']}")
                    
                    if test_perf['score'] > best_score:
                        best_score = test_perf['score']
                        best_params = test_params.copy()
            
            if best_params != strat_info['default_params']:
                print(f"  最佳參數: {best_params} (評分: {best_score})")
                all_results[strat_name]['optimized_params'] = best_params
                all_results[strat_name]['optimized_score'] = best_score
    
    # 排名
    print(f"\n{'=' * 80}")
    print("策略排名")
    print(f"{'=' * 80}")
    
    ranked = sorted(all_results.items(), key=lambda x: x[1]['performance']['score'], reverse=True)
    
    print(f"\n{'排名':4s} {'策略':12s} {'勝率':>6s} {'平均報酬':>8s} {'PF':>6s} {'評分':>6s}")
    print("-" * 50)
    
    for rank, (name, data) in enumerate(ranked, 1):
        p = data['performance']
        print(f"{rank:4d} {STRATEGIES[name]['name']:12s} {p['win_rate']:5.1f}% {p['avg_return']:+7.2f}% {p['profit_factor']:6.2f} {p['score']:6.2f}")
    
    # 儲存結果
    save_strategy_state(all_results)
    
    return all_results


def save_strategy_state(results):
    """儲存策略狀態"""
    state = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'strategies': {}
    }
    
    for name, data in results.items():
        state['strategies'][name] = {
            'performance': data['performance'],
            'params': data.get('optimized_params', data['params']),
            'default_params': STRATEGIES[name]['default_params'],
        }
    
    # 計算最優權重 (用於綜合選股)
    ranked = sorted(results.items(), key=lambda x: x[1]['performance']['score'], reverse=True)
    total_score = sum(max(d['performance']['score'], 0.01) for _, d in ranked)
    
    weights = {}
    for name, data in ranked:
        w = max(data['performance']['score'], 0.01) / total_score if total_score > 0 else 1.0 / len(ranked)
        weights[name] = round(w, 4)
    
    state['strategy_weights'] = weights
    
    with open(STRATEGY_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n策略狀態已儲存: {STRATEGY_STATE_FILE}")
    print(f"\n策略權重:")
    for name, w in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        print(f"  {STRATEGIES[name]['name']:12s}: {w:.1%}")


def load_strategy_state():
    """載入策略狀態"""
    if STRATEGY_STATE_FILE.exists():
        with open(STRATEGY_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


if __name__ == "__main__":
    run_full_backtest()
