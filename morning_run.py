#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日盤前自動執行 - 雙策略選股版"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import argparse
import json
import time
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime

from src.data.yahoo_fetcher import YahooFetcher
from strategy_backtest import load_strategy_state, prepare_data
from src.dual_strategy import SwingStrategy, InvestStrategy

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "morning_run.log"
RESULT_FILE = BASE_DIR / "today_picks.json"


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def load_stocks():
    """載入股票池"""
    universe_file = BASE_DIR / "stock_universe.json"
    if universe_file.exists():
        with open(universe_file) as f:
            universe = json.load(f)
        twse_stocks = universe.get('twse', [])
        tpex_stocks = universe.get('tpex', [])
        log(f"股票池: 上市 {len(twse_stocks)} 檔 (上櫃 {len(tpex_stocks)} 檔已排除)")
        return twse_stocks
    fallback = [
        '2330', '2317', '2454', '2308', '2412', '2881', '2882', '2886', '2891',
        '8046', '2486', '3189', '3037', '2337', '2344', '2603', '1301', '2002',
    ]
    log(f"股票池: 預設 {len(fallback)} 檔 (無 stock_universe.json)")
    return fallback


def fetch_stock_data(sid, yf_yf_fetcher):
    """取得個股技術面資料，Yahoo 失敗時 fallback 到 TWSE"""
    try:
        symbol = f"{sid}.TW"
        df = yf_yf_fetcher.get_stock_data(symbol, period='3mo')
        if df.empty or len(df) < 20:
            raise ValueError("insufficient data")
        return prepare_data(df)
    except Exception:
        pass

    try:
        from src.data.yf_fetcher import TWSEFetcher
        yf_fetcher = TWSEFetcher()
        df = yf_fetcher.get_historical_price(sid, months=2)
        if df.empty or len(df) < 20:
            raise ValueError("insufficient data")
        log(f"  {sid}: TWSE fallback 成功")
        time.sleep(3)
        return prepare_data(df)
    except Exception:
        return None


def fetch_financial_data(sid):
    """取得基本面資料（含 DCF），用於投資策略"""
    try:
        from dcf_analysis import get_financial_data, calculate_dcf
        fin = get_financial_data(sid)
        if not fin:
            return None
        dcf = calculate_dcf(fin)
        if dcf:
            fin['dcf_value'] = dcf.get('intrinsic_value', 0)
            fin['dcf_margin'] = dcf.get('safety_margin', 0)
        return fin
    except Exception as e:
        # log(f"DCF 失敗 {sid}: {e}")
        return None


def run_swing(stocks, yf_fetcher):
    """執行短線策略"""
    strategy = SwingStrategy()
    log(f"\n{'='*60}")
    log(f"策略: {strategy.name} — {strategy.description}")
    log(f"{'='*60}")

    results = []
    failed = []

    for sid in stocks:
        df = fetch_stock_data(sid, yf_fetcher)
        if df is None:
            failed.append(sid)
            time.sleep(0.5)
            continue

        score_result = strategy.score(df)
        if score_result is None:
            failed.append(sid)
            continue

        rec = strategy.make_recommendation({**score_result, 'stock_id': sid})
        rec['stock_id'] = sid
        results.append(rec)
        time.sleep(0.2)

    results.sort(key=lambda x: x['score'], reverse=True)

    buys = [r for r in results if r['score'] >= 65]
    watches = [r for r in results if 50 <= r['score'] < 65]

    log(f"\n短線分析完成: {len(results)}/{len(stocks)} 檔 (失敗: {len(failed)})")
    if buys:
        log(f"\n強勢候選 ({len(buys)} 檔):")
        for r in buys:
            log(f"  {r['stock_id']}: {r['close']:.0f}元 評分{r['score']} "
                f"RSI{r['rsi']} {r['ma_trend']} | "
                f"進場{r.get('entry','-')} 停損{r.get('stop_loss','-')} 目標{r.get('target','-')}")
    else:
        log("\n無強勢候選")

    if watches:
        log(f"\n觀察 ({len(watches)} 檔):")
        for r in watches[:8]:
            log(f"  {r['stock_id']}: {r['close']:.0f}元 評分{r['score']} RSI{r['rsi']} {r['ma_trend']}")

    return {
        'strategy': 'swing',
        'strategy_name': strategy.name,
        'total_analyzed': len(results),
        'failed': failed,
        'buys': buys,
        'watches': watches[:8],
        'avoids': [{'stock_id': r['stock_id'], 'score': r['score']}
                   for r in results if r['score'] < 40],
        'all_results': results,
    }


def run_invest(stocks, yf_fetcher):
    """執行投資佈局策略"""
    strategy = InvestStrategy()
    log(f"\n{'='*60}")
    log(f"策略: {strategy.name} — {strategy.description}")
    log(f"{'='*60}")

    results = []
    failed = []

    for sid in stocks:
        df = fetch_stock_data(sid, yf_fetcher)
        if df is None:
            failed.append(sid)
            time.sleep(0.5)
            continue

        fin_data = fetch_financial_data(sid)
        score_result = strategy.score(df, fin_data=fin_data)
        if score_result is None:
            failed.append(sid)
            continue

        rec = strategy.make_recommendation({**score_result, 'stock_id': sid})
        rec['stock_id'] = sid
        if fin_data:
            rec['name'] = fin_data.get('name', sid)
            rec['sector'] = fin_data.get('sector', '')
            rec['pe'] = fin_data.get('pe', 0)
            rec['dividend_yield'] = round(fin_data.get('dividend_yield', 0) * 100, 2)
            rec['revenue_growth'] = round(fin_data.get('revenue_growth', 0) * 100, 1)
            rec['dcf_value'] = fin_data.get('dcf_value')
            rec['dcf_margin'] = fin_data.get('dcf_margin')
        results.append(rec)
        time.sleep(0.3)

    results.sort(key=lambda x: x['score'], reverse=True)

    buys = [r for r in results if r['score'] >= 65]
    watches = [r for r in results if 50 <= r['score'] < 65]

    log(f"\n投資分析完成: {len(results)}/{len(stocks)} 檔 (失敗: {len(failed)})")
    if buys:
        log(f"\n價值低估 ({len(buys)} 檔):")
        for r in buys:
            iv = f"內在{r['intrinsic_value']:.0f}" if r.get('intrinsic_value') else ""
            sm = f"邊際{r['safety_margin']:+.1f}%" if r.get('safety_margin') is not None else ""
            log(f"  {r['stock_id']}: {r['close']:.0f}元 評分{r['score']} "
                f"{iv} {sm} | {r.get('action', '')}")
    else:
        log("\n無價值低估標的")

    if watches:
        log(f"\n觀察佈局 ({len(watches)} 檔):")
        for r in watches[:8]:
            sm = f"邊際{r['safety_margin']:+.1f}%" if r.get('safety_margin') is not None else ""
            log(f"  {r['stock_id']}: {r['close']:.0f}元 評分{r['score']} {sm}")

    return {
        'strategy': 'invest',
        'strategy_name': strategy.name,
        'total_analyzed': len(results),
        'failed': failed,
        'buys': buys,
        'watches': watches[:8],
        'avoids': [{'stock_id': r['stock_id'], 'score': r['score']}
                   for r in results if r['score'] < 40],
        'all_results': results,
    }


def run(strategy='both'):
    today = datetime.now().strftime('%Y-%m-%d')
    log(f"=== 盤前選股開始 ({today}) 策略: {strategy} ===")

    stocks = load_stocks()
    
    output = {
        'date': today,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'strategy': strategy,
    }

    yf_fetcher = YahooFetcher()

    if strategy in ('swing', 'both'):
        swing_result = run_swing(stocks, yf_fetcher)
        output['swing'] = swing_result

    if strategy in ('invest', 'both'):
        invest_result = run_invest(stocks, yf_fetcher)
        output['invest'] = invest_result

    # 儲存結果
    with open(RESULT_FILE, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    log(f"\n結果儲存: {RESULT_FILE}")

    # 生成分析報告
    try:
        from report_generator import generate_dual_report
        generate_dual_report(output)
        log(f"\n分析報告已生成")
    except Exception as e:
        log(f"報告生成失敗: {e}")

    # Ollama 摘要
    try:
        from token_stats import query_ollama
        swing_buys = len(output.get('swing', {}).get('buys', []))
        invest_buys = len(output.get('invest', {}).get('buys', []))
        total = sum(r.get('total_analyzed', 0) for r in [output.get('swing', {}), output.get('invest', {})])
        summary_prompt = (
            f"用繁體中文簡短總結今日雙策略選股：分析{total}檔，"
            f"短線候選{swing_buys}檔，投資候選{invest_buys}檔。用3行以內回答。"
        )
        ollama_result = query_ollama(summary_prompt)
        if 'response' in ollama_result:
            log(f"\n[Ollama 摘要] {ollama_result['response'][:200]}")
            log(f"[省 token: {ollama_result['total_tokens']}]")
    except Exception as e:
        log(f"Ollama 摘要失敗: {e}")

    log(f"=== 盤前選股完成 ===")
    return output


def parse_args():
    parser = argparse.ArgumentParser(description='每日盤前雙策略選股')
    parser.add_argument(
        '--strategy', '-s',
        choices=['swing', 'invest', 'both'],
        default='both',
        help='選股策略: swing(短線), invest(投資), both(雙策略, 預設)',
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(strategy=args.strategy)
