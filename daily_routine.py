#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日自動化流程 - 回測、選股、追蹤"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from datetime import datetime
import json

def morning():
    """盤前流程 (08:30)"""
    print(f"=== 盤前流程 {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    
    state_file = Path(__file__).parent / "strategy_state.json"
    
    # 1. 檢查是否需要重新回測 (每週一或首次)
    need_backtest = False
    if not state_file.exists():
        need_backtest = True
        print("首次執行，需要回測\n")
    else:
        with open(state_file) as f:
            state = json.load(f)
        last = datetime.strptime(state['last_updated'], '%Y-%m-%d %H:%M:%S')
        days_since = (datetime.now() - last).days
        if days_since >= 7 or datetime.now().weekday() == 0:
            need_backtest = True
            print(f"距上次回測 {days_since} 天，重新回測\n")
    
    if need_backtest:
        print("--- 執行策略回測 ---\n")
        from strategy_backtest import run_full_backtest
        run_full_backtest()
        print()
    
    # 2. 追蹤昨日選股表現
    print("--- 追蹤選股績效 ---\n")
    from smart_screener import track_performance
    track_performance()
    print()
    
    # 3. 今日選股
    print("--- 執行智能選股 ---\n")
    from smart_screener import smart_screen
    smart_screen()


def aftermarket():
    """盤後流程 (14:30)"""
    print(f"=== 盤後流程 {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    
    # 追蹤今日表現
    from smart_screener import track_performance
    track_performance()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else 'morning'
    
    if mode == 'morning':
        morning()
    elif mode == 'aftermarket':
        aftermarket()
    elif mode == 'backtest':
        from strategy_backtest import run_full_backtest
        run_full_backtest()
    elif mode == 'screen':
        from smart_screener import smart_screen
        smart_screen()
    elif mode == 'track':
        from smart_screener import track_performance
        track_performance()
    else:
        print(f"未知模式: {mode}")
        print("可用: morning, aftermarket, backtest, screen, track")
