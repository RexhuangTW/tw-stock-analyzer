#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""📅 每週回顧 - 自動整理與分析"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import json
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

# ==================== 設定 ====================

MEMORY_DIR = Path.home() / ".openclaw/workspace/memory"
WORKSPACE = Path.home() / ".openclaw/workspace"
SCREENING_DIR = Path(__file__).parent / "screening_results"
STATE_FILE = Path(__file__).parent / "heartbeat_state.json"

# ==================== 主程式 ====================

def weekly_review():
    """每週回顧"""
    
    print("📅 開始每週回顧...")
    print("=" * 80)
    
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday() + 1)  # 上週一
    week_end = today - timedelta(days=today.weekday() - 5)     # 上週日
    
    week_str = f"{week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}"
    print(f"📆 回顧週次: {week_str}\n")
    
    # === 1. 統計選股成效 ===
    print("📊 統計選股成效...")
    
    screenings = []
    for day in range(7):
        date = week_start + timedelta(days=day)
        date_str = date.strftime('%Y-%m-%d')
        screening_file = SCREENING_DIR / f"screening_{date_str}.md"
        
        if screening_file.exists():
            screenings.append(date_str)
    
    print(f"  本週執行選股: {len(screenings)}/7 天")
    for s in screenings:
        print(f"    ✓ {s}")
    
    # === 2. 整理 memory ===
    print("\n📝 整理每日記憶...")
    
    daily_memories = []
    for day in range(7):
        date = week_start + timedelta(days=day)
        date_str = date.strftime('%Y-%m-%d')
        memory_file = MEMORY_DIR / f"{date_str}.md"
        
        if memory_file.exists():
            daily_memories.append(date_str)
    
    print(f"  本週記憶檔案: {len(daily_memories)}/7 天")
    
    # === 3. 生成週報 ===
    print("\n📄 生成週報...")
    
    report = f"""# 📊 每週回顧 - {week_str}

**生成時間:** {today.strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 選股統計

- **執行天數:** {len(screenings)}/7
- **執行日期:** {', '.join(screenings)}

## 📝 工作記錄

- **Memory 檔案:** {len(daily_memories)}/7

## 🎯 下週計畫

- 持續每日選股
- 追蹤選股成效
- 優化策略參數

## 💡 改進建議

(待自動分析)

---

## 📋 本週 Memory 摘要

"""
    
    # 加入每日摘要
    for date_str in daily_memories:
        memory_file = MEMORY_DIR / f"{date_str}.md"
        content = memory_file.read_text(encoding='utf-8')
        
        # 提取重要事項 (簡化版)
        lines = content.split('\n')
        important_lines = [l for l in lines if any(kw in l for kw in ['✅', '❌', '🔥', '⭐', '重要'])]
        
        if important_lines:
            report += f"\n### {date_str}\n\n"
            for line in important_lines[:5]:  # 最多 5 項
                report += f"{line}\n"
    
    report += "\n---\n\n**下次回顧:** " + (today + timedelta(days=7)).strftime('%Y-%m-%d')
    
    # 儲存週報
    report_file = WORKSPACE / f"weekly_review_{week_start.strftime('%Y-W%W')}.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"\n✅ 週報已生成: {report_file}")
    
    # === 4. 更新 MEMORY.md (長期記憶) ===
    print("\n🧠 更新長期記憶...")
    
    memory_md = WORKSPACE / "MEMORY.md"
    
    if memory_md.exists():
        content = memory_md.read_text(encoding='utf-8')
        
        # 加入週報連結
        week_entry = f"\n## {week_str}\n\n- [週報]({report_file.name})\n"
        
        # 簡單地加在最後 (可以改進為智能插入)
        memory_md.write_text(content + week_entry, encoding='utf-8')
        print("✅ MEMORY.md 已更新")
    
    # === 5. 策略表現分析 ===
    print("\n🤖 分析策略表現...")
    
    # TODO: 實作策略勝率統計
    # 需要追蹤每次選股結果的後續表現
    
    print("=" * 80)
    print("✅ 每週回顧完成！\n")
    print(f"📄 週報: {report_file}")

if __name__ == "__main__":
    weekly_review()
