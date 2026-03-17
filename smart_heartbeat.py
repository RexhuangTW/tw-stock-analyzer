#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🤖 智能 Heartbeat - 自動化任務執行引擎"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import json
import pandas as pd
from datetime import datetime, timedelta
import subprocess

# ==================== 設定 ====================

STATE_FILE = Path(__file__).parent / "heartbeat_state.json"
MEMORY_DIR = Path.home() / ".openclaw/workspace/memory"
WORKSPACE = Path.home() / ".openclaw/workspace"
TODO_FILE = WORKSPACE / "TODO.md"

# ==================== 狀態管理 ====================

def load_state():
    """載入狀態"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_screening": None,
        "last_review": None,
        "last_notification": None,
        "screening_success_rate": 0.0,
        "total_screenings": 0,
        "parameters": {
            "rsi_threshold": 35,
            "multi_factor_min": 60,
            "lookback_days": 20
        },
        "strategy_performance": {}
    }

def save_state(state):
    """儲存狀態"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

# ==================== 早上任務 ====================

def morning_routine():
    """早上例行任務 (08:00-09:00)"""
    print("🌅 執行早上例行任務...")
    
    state = load_state()
    today = datetime.now().strftime('%Y-%m-%d')
    
    notifications = []
    
    # === 1. 檢查是否已執行選股 ===
    if state.get('last_screening') != today:
        print("📊 執行每日選股...")
        
        try:
            result = subprocess.run(
                ['python3', 'daily_screener.py'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                state['last_screening'] = today
                state['total_screenings'] += 1
                
                # 檢查是否有重點推薦
                screening_file = Path(__file__).parent / f"screening_results/screening_{today}.md"
                if screening_file.exists():
                    content = screening_file.read_text(encoding='utf-8')
                    if '⭐️ 重點推薦' in content and '出現次數' in content:
                        notifications.append("📊 今日選股有重點推薦股票！")
                
                print("✅ 選股完成")
            else:
                print(f"❌ 選股失敗: {result.stderr}")
        
        except Exception as e:
            print(f"❌ 選股錯誤: {e}")
    else:
        print("✅ 今日已執行選股")
    
    # === 2. 檢查 TODO ===
    if TODO_FILE.exists():
        content = TODO_FILE.read_text(encoding='utf-8')
        if today in content or '今天' in content or '今日' in content:
            notifications.append(f"📝 TODO 有今日待辦事項")
    
    # === 3. 整理昨日 memory ===
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_memory = MEMORY_DIR / f"{yesterday}.md"
    
    if yesterday_memory.exists() and state.get('last_memory_organize') != yesterday:
        print(f"📝 整理昨日記憶: {yesterday}")
        # TODO: 可以加入自動摘要功能
        state['last_memory_organize'] = yesterday
    
    # === 4. 發送通知 ===
    if notifications:
        print("\n🔔 重要通知:")
        for notif in notifications:
            print(f"  {notif}")
        
        # 寫入日報
        report_file = WORKSPACE / f"daily_report_{today}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📋 每日報告 - {today}\n\n")
            f.write(f"**生成時間:** {datetime.now().strftime('%H:%M:%S')}\n\n")
            for notif in notifications:
                f.write(f"- {notif}\n")
        
        state['last_notification'] = today
    
    save_state(state)
    
    if notifications:
        return f"🌅 早安！今日有 {len(notifications)} 項重要事項"
    return "HEARTBEAT_OK"

# ==================== 盤中任務 ====================

def intraday_routine():
    """盤中監控 (09:00-13:30)"""
    print("📊 執行盤中監控...")
    
    now = datetime.now()
    
    # 只在交易時段執行
    if not (9 <= now.hour < 14):
        return "HEARTBEAT_OK"
    
    # TODO: 實作盤中監控邏輯
    # - 監控選股股票表現
    # - 價格觸發警報
    # - 異常波動偵測
    
    return "HEARTBEAT_OK"

# ==================== 盤後任務 ====================

def aftermarket_routine():
    """盤後整理 (14:00-15:00)"""
    print("🌆 執行盤後整理...")
    
    state = load_state()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # === 1. 記錄今日盤勢 ===
    memory_file = MEMORY_DIR / f"{today}.md"
    
    # 如果 memory 檔案不存在，建立初始結構
    if not memory_file.exists():
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        memory_file.write_text(f"""# {today} 工作日誌

## 📊 盤勢記錄

- 加權指數: (待更新)
- 漲跌: (待更新)
- 成交量: (待更新)

## 🔍 選股結果

- 執行時間: {datetime.now().strftime('%H:%M')}
- 重點股票: (檢查 screening_results/)

## 📝 重要事項

(待補充)

---
""", encoding='utf-8')
    
    # === 2. 更新選股成效 ===
    # TODO: 追蹤今日選股股票的表現
    
    save_state(state)
    
    return "HEARTBEAT_OK"

# ==================== 晚間任務 ====================

def evening_routine():
    """晚間回顧 (21:00)"""
    print("🌙 執行晚間回顧...")
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # === 1. 生成日報 ===
    report_file = WORKSPACE / f"daily_summary_{today}.md"
    
    summary = f"""# 📊 每日總結 - {today}

## ✅ 今日完成

- 選股執行: ✓
- Memory 整理: ✓

## 📈 市場記錄

(待補充)

## 📝 明日計畫

- 繼續監控選股結果
- 檢查 TODO 事項

---
**生成時間:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    report_file.write_text(summary, encoding='utf-8')
    
    return "HEARTBEAT_OK"

# ==================== 完全自主 (階段 3) ====================

def autonomous_optimization():
    """自主學習與優化"""
    print("🤖 執行自主優化...")
    
    state = load_state()
    params = state['parameters']
    performance = state.get('strategy_performance', {})
    
    # === 1. 分析策略表現 ===
    # TODO: 根據歷史數據計算各策略勝率
    
    # === 2. 自動調整參數 ===
    # 範例邏輯：
    # - RSI 策略勝率 < 40% → 降低 threshold (更嚴格)
    # - RSI 策略勝率 > 70% → 提高 threshold (放寬)
    
    adjustments = []
    
    # RSI 自動調整
    rsi_perf = performance.get('rsi_oversold', {})
    if rsi_perf.get('trades', 0) >= 10:
        win_rate = rsi_perf.get('win_rate', 0.5)
        current_threshold = params['rsi_threshold']
        
        if win_rate < 0.4 and current_threshold > 25:
            params['rsi_threshold'] -= 5
            adjustments.append(f"RSI threshold: {current_threshold} → {params['rsi_threshold']} (勝率低，更嚴格)")
        elif win_rate > 0.7 and current_threshold < 45:
            params['rsi_threshold'] += 5
            adjustments.append(f"RSI threshold: {current_threshold} → {params['rsi_threshold']} (勝率高，放寬)")
    
    # 多因子自動調整
    multi_perf = performance.get('multi_factor', {})
    if multi_perf.get('trades', 0) >= 10:
        win_rate = multi_perf.get('win_rate', 0.5)
        current_min = params['multi_factor_min']
        
        if win_rate < 0.4 and current_min < 75:
            params['multi_factor_min'] += 5
            adjustments.append(f"Multi-factor min: {current_min} → {params['multi_factor_min']} (提高門檻)")
        elif win_rate > 0.7 and current_min > 50:
            params['multi_factor_min'] -= 5
            adjustments.append(f"Multi-factor min: {current_min} → {params['multi_factor_min']} (降低門檻)")
    
    # === 3. 儲存調整 ===
    if adjustments:
        print("\n🔧 自動調整參數:")
        for adj in adjustments:
            print(f"  {adj}")
        
        state['parameters'] = params
        save_state(state)
        
        # 記錄到 memory
        today = datetime.now().strftime('%Y-%m-%d')
        memory_file = MEMORY_DIR / f"{today}.md"
        
        adjustment_log = f"\n## 🤖 自動優化 ({datetime.now().strftime('%H:%M')})\n\n"
        for adj in adjustments:
            adjustment_log += f"- {adj}\n"
        
        if memory_file.exists():
            content = memory_file.read_text(encoding='utf-8')
            memory_file.write_text(content + adjustment_log, encoding='utf-8')
    
    return "HEARTBEAT_OK"

# ==================== 主程式 ====================

def main():
    """主程式 - 根據時間或參數執行對應任務"""
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        # 自動判斷時段
        hour = datetime.now().hour
        if 8 <= hour < 9:
            mode = 'morning'
        elif 9 <= hour < 14:
            mode = 'intraday'
        elif 14 <= hour < 15:
            mode = 'aftermarket'
        elif hour == 21:
            mode = 'evening'
        else:
            mode = 'auto'
    
    print(f"🤖 Smart Heartbeat - Mode: {mode}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    result = "HEARTBEAT_OK"
    
    if mode == 'morning':
        result = morning_routine()
    elif mode == 'intraday':
        result = intraday_routine()
    elif mode == 'aftermarket':
        result = aftermarket_routine()
    elif mode == 'evening':
        result = evening_routine()
    elif mode == 'optimize':
        result = autonomous_optimization()
    elif mode == 'auto':
        # 自動判斷該執行什麼
        hour = datetime.now().hour
        if 8 <= hour < 9:
            result = morning_routine()
        elif hour == 21:
            result = evening_routine()
    
    print("=" * 60)
    print(f"✅ Result: {result}")
    
    return result

if __name__ == "__main__":
    main()
