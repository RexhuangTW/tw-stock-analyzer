#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日盤前自動執行 - 簡單可靠版"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import json
import time
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime

from src.data.yahoo_fetcher import YahooFetcher
from src.indicators.technical import calculate_ma, calculate_rsi, calculate_macd, calculate_bollinger_bands
from strategy_backtest import load_strategy_state, prepare_data

LOG_FILE = Path(__file__).parent / "morning_run.log"
RESULT_FILE = Path(__file__).parent / "today_picks.json"

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def run():
    today = datetime.now().strftime('%Y-%m-%d')
    log(f"=== 盤前選股開始 ({today}) ===")
    
    # 載入策略權重
    state = load_strategy_state()
    if state:
        weights = state.get('strategy_weights', {})
        log(f"使用回測權重 (更新: {state['last_updated']})")
    else:
        weights = {'rsi_oversold': 0.3, 'golden_cross': 0.2, 'bollinger_lower': 0.17,
                   'multi_trend': 0.13, 'macd_cross': 0.11, 'composite': 0.09}
        log("無回測資料，使用預設權重")
    
    # 載入完整股票池
    universe_file = Path(__file__).parent / "stock_universe.json"
    if universe_file.exists():
        with open(universe_file) as f:
            universe = json.load(f)
        twse_stocks = universe.get('twse', [])
        tpex_stocks = universe.get('tpex', [])
        stocks = twse_stocks + tpex_stocks
        log(f"股票池: 上市 {len(twse_stocks)} + 上櫃 {len(tpex_stocks)} = {len(stocks)} 檔")
    else:
        stocks = [
            '2330','2317','2454','2308','2412','2881','2882','2886','2891',
            '8046','2486','3189','3037','2337','2344','2603','1301','2002',
        ]
        log(f"股票池: 預設 {len(stocks)} 檔 (無 stock_universe.json)")
    
    yf = YahooFetcher()
    results = []
    failed = []
    
    for sid in stocks:
        try:
            # 上市 .TW, 上櫃 .TWO
            if universe_file.exists():
                suffix = '.TWO' if sid in tpex_stocks else '.TW'
            else:
                suffix = '.TW'
            symbol = f"{sid}{suffix}"
            df = yf.get_stock_data(symbol, period='3mo')
            if df.empty or len(df) < 20:
                failed.append(sid)
                continue
            
            df = prepare_data(df)
            l = df.iloc[-1]
            p = df.iloc[-2]
            
            # 評分
            score = 0
            
            # RSI (權重最高)
            w_rsi = weights.get('rsi_oversold', 0.3)
            if l['rsi'] < 25: score += 3 * w_rsi
            elif l['rsi'] < 35: score += 1.5 * w_rsi
            elif l['rsi'] < 50: score += 0.5 * w_rsi
            elif l['rsi'] > 70: score -= 1 * w_rsi
            
            # 均線
            w_ma = weights.get('golden_cross', 0.2) + weights.get('multi_trend', 0.13)
            if l['close'] > l['ma5'] > l['ma20']: score += 2 * w_ma
            elif l['close'] > l['ma20']: score += 1 * w_ma
            elif l['close'] < l['ma5'] < l['ma20']: score -= 2 * w_ma
            
            # MACD
            w_macd = weights.get('macd_cross', 0.11)
            if l['macd_hist'] > 0 and l['macd_hist'] > p['macd_hist']: score += 2 * w_macd
            elif l['macd_hist'] > 0: score += 1 * w_macd
            elif l['macd_hist'] < 0: score -= 1 * w_macd
            
            # 布林
            w_bb = weights.get('bollinger_lower', 0.17)
            if l['close'] <= l['bb_lower']: score += 3 * w_bb
            elif l['close'] >= l['bb_upper']: score -= 1 * w_bb
            
            # 正規化 0-100
            max_s = 3 * (w_rsi + w_ma + w_macd + w_bb)
            min_s = -2 * (w_rsi + w_ma + w_macd + w_bb)
            normalized = (score - min_s) / (max_s - min_s) * 100 if (max_s - min_s) > 0 else 50
            
            ma_trend = '多頭' if l['close'] > l['ma5'] > l['ma20'] else '空頭' if l['close'] < l['ma5'] < l['ma20'] else '盤整'
            change = (l['close'] - p['close']) / p['close'] * 100
            
            results.append({
                'stock_id': sid,
                'close': float(l['close']),
                'change_pct': round(change, 2),
                'rsi': round(float(l['rsi']), 1),
                'ma_trend': ma_trend,
                'score': round(normalized, 1),
                'macd_hist': round(float(l['macd_hist']), 2),
            })
            
            time.sleep(0.2)
        except Exception as e:
            # Yahoo 失敗就嘗試 TWSE
            try:
                from src.data.fetcher import TWSEFetcher
                fetcher = TWSEFetcher()
                df = fetcher.get_historical_price(sid, months=2)
                if df.empty or len(df) < 20:
                    raise ValueError("no data")
                df = prepare_data(df)
                l = df.iloc[-1]
                p = df.iloc[-2]
                
                score = 0
                w_rsi = weights.get('rsi_oversold', 0.3)
                if l['rsi'] < 25: score += 3 * w_rsi
                elif l['rsi'] < 35: score += 1.5 * w_rsi
                elif l['rsi'] < 50: score += 0.5 * w_rsi
                elif l['rsi'] > 70: score -= 1 * w_rsi
                
                w_ma = weights.get('golden_cross', 0.2) + weights.get('multi_trend', 0.13)
                if l['close'] > l['ma5'] > l['ma20']: score += 2 * w_ma
                elif l['close'] > l['ma20']: score += 1 * w_ma
                elif l['close'] < l['ma5'] < l['ma20']: score -= 2 * w_ma
                
                w_macd = weights.get('macd_cross', 0.11)
                if l['macd_hist'] > 0 and l['macd_hist'] > p['macd_hist']: score += 2 * w_macd
                elif l['macd_hist'] > 0: score += 1 * w_macd
                elif l['macd_hist'] < 0: score -= 1 * w_macd
                
                w_bb = weights.get('bollinger_lower', 0.17)
                if l['close'] <= l['bb_lower']: score += 3 * w_bb
                elif l['close'] >= l['bb_upper']: score -= 1 * w_bb
                
                max_s = 3 * (w_rsi + w_ma + w_macd + w_bb)
                min_s = -2 * (w_rsi + w_ma + w_macd + w_bb)
                normalized = (score - min_s) / (max_s - min_s) * 100 if (max_s - min_s) > 0 else 50
                
                ma_trend = '多頭' if l['close'] > l['ma5'] > l['ma20'] else '空頭' if l['close'] < l['ma5'] < l['ma20'] else '盤整'
                change = (l['close'] - p['close']) / p['close'] * 100
                
                results.append({
                    'stock_id': sid, 'close': float(l['close']), 'change_pct': round(change, 2),
                    'rsi': round(float(l['rsi']), 1), 'ma_trend': ma_trend,
                    'score': round(normalized, 1), 'macd_hist': round(float(l['macd_hist']), 2),
                })
                log(f"  {sid}: TWSE fallback 成功")
                time.sleep(3)
                continue
            except:
                pass
            failed.append(f"{sid}")
            time.sleep(0.5)
    
    # 排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 分類
    buys = [r for r in results if r['score'] >= 65]
    watches = [r for r in results if 50 <= r['score'] < 65]
    avoids = [r for r in results if r['score'] < 40]
    
    # 輸出
    log(f"\n分析完成: {len(results)}/{len(stocks)} 檔 (失敗: {len(failed)})")
    
    if buys:
        log(f"\n買進候選 ({len(buys)} 檔):")
        for r in buys:
            log(f"  {r['stock_id']}: {r['close']:.0f}元 評分{r['score']} RSI{r['rsi']} {r['ma_trend']}")
    else:
        log("\n無買進候選")
    
    if watches:
        log(f"\n觀察名單 ({len(watches)} 檔):")
        for r in watches[:8]:
            log(f"  {r['stock_id']}: {r['close']:.0f}元 評分{r['score']} RSI{r['rsi']} {r['ma_trend']}")
    
    if avoids:
        log(f"\n避開 ({len(avoids)} 檔):")
        for r in avoids:
            log(f"  {r['stock_id']}: 評分{r['score']} {r['ma_trend']}")
    
    # 儲存結果
    output = {
        'date': today,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_analyzed': len(results),
        'failed': failed,
        'buys': buys,
        'watches': watches[:8],
        'avoids': [{'stock_id': r['stock_id'], 'score': r['score']} for r in avoids],
    }
    
    with open(RESULT_FILE, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    log(f"\n結果儲存: {RESULT_FILE}")
    
    # 第二階段: DCF 基本面分析 (只分析觀察名單)
    if buys or watches:
        log(f"\n--- DCF 基本面分析 ---")
        try:
            from dcf_analysis import analyze_watchlist
            dcf_targets = buys + watches[:8]
            dcf_results = analyze_watchlist(dcf_targets)
            
            if dcf_results:
                for r in dcf_results:
                    iv = f"{r['intrinsic_value']:.0f}" if r['intrinsic_value'] else "N/A"
                    sm = f"{r['safety_margin']:+.1f}%" if r['safety_margin'] is not None else "N/A"
                    log(f"  {r['stock_id']} {r['name'][:8]}: 綜合{r['combined_score']:.0f} 內在{iv} 邊際{sm} {r['recommendation']}")
                
                output['dcf_results'] = dcf_results
        except Exception as e:
            log(f"  DCF 分析失敗: {e}")
    
    log(f"=== 盤前選股完成 ===")
    
    return output

if __name__ == "__main__":
    run()
