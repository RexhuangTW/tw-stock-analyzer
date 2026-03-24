#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""選股報告生成器 - 產出帶分析的每日報告"""

import json
from pathlib import Path
from datetime import datetime

NAMES_FILE = Path(__file__).parent / "stock_names.json"
PICKS_FILE = Path(__file__).parent / "today_picks.json"
REPORT_FILE = Path(__file__).parent / "daily_report.md"

def load_names():
    if NAMES_FILE.exists():
        with open(NAMES_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_name(stock_id, names, fallback=""):
    return names.get(stock_id, fallback)

def generate_report():
    """生成每日選股分析報告"""
    
    picks_file = PICKS_FILE
    if not picks_file.exists():
        return "無選股資料"
    
    with open(picks_file) as f:
        picks = json.load(f)
    
    names = load_names()
    date = picks.get('date', datetime.now().strftime('%Y-%m-%d'))
    total = picks.get('total_analyzed', 0)
    buys = picks.get('buys', [])
    watches = picks.get('watches', [])
    avoids = picks.get('avoids', [])
    dcf_results = picks.get('dcf_results', [])
    
    # 統計
    bullish = len([w for w in watches if w.get('ma_trend') == '多頭'])
    bearish = len(avoids)
    
    report = []
    report.append(f"# 每日選股報告 ({date})")
    report.append("")
    report.append("---")
    report.append("")
    
    # 市場概況
    report.append("## 市場概況")
    report.append("")
    report.append(f"- 分析標的: {total} 檔 (上市)")
    report.append(f"- 多頭股數: {bullish} 檔")
    report.append(f"- 空頭/避開: {bearish} 檔")
    report.append(f"- 多空比: {bullish}:{bearish}")
    
    if bearish > total * 0.5:
        report.append(f"- 判斷: 市場偏空，超過半數股票在避開名單")
    elif bullish > bearish:
        report.append(f"- 判斷: 市場偏多")
    else:
        report.append(f"- 判斷: 多空交戰")
    report.append("")
    
    # DCF 雙重驗證結果
    if dcf_results:
        report.append("## DCF 雙重驗證")
        report.append("")
        
        buy_candidates = [r for r in dcf_results if '買進' in r.get('recommendation', '')]
        watch_candidates = [r for r in dcf_results if '觀察' in r.get('recommendation', '')]
        avoid_candidates = [r for r in dcf_results if '避開' in r.get('recommendation', '')]
        
        if buy_candidates:
            report.append("### 買進候選")
            report.append("")
            
            for r in buy_candidates:
                sid = r['stock_id']
                name = get_name(sid, names, r.get('name', sid))
                price = r['price']
                score = r['combined_score']
                iv = r.get('intrinsic_value')
                sm = r.get('safety_margin')
                pe = r.get('pe', 0)
                dy = r.get('dividend_yield', 0)
                rg = r.get('revenue_growth', 0)
                sector = r.get('sector', '')
                
                report.append(f"**{sid} {name}** | {price:.0f} 元 | 綜合 {score:.0f} 分 | 安全邊際 {sm:+.1f}%")
                report.append("")
                
                # 產業
                if sector:
                    report.append(f"- 產業: {sector}")
                
                # 為什麼選中
                report.append("- 選中原因:")
                if sm and sm > 0:
                    report.append(f"  - DCF 內在價值 {iv:.0f} 元，目前 {price:.0f} 元被低估 {sm:.0f}%")
                
                tech_score = r.get('tech_score', 0)
                if tech_score >= 60:
                    report.append(f"  - 技術面評分 {tech_score:.0f}，均線多頭排列")
                
                if pe > 0 and pe < 15:
                    report.append(f"  - PE {pe:.1f}x 偏低，估值合理")
                
                if 1 < dy < 15:  # 排除異常數據
                    report.append(f"  - 殖利率 {dy:.1f}%，有股息保護")
                
                if rg > 10:
                    report.append(f"  - 營收成長 {rg:.1f}%，成長動能佳")
                
                # 風險
                report.append("- 風險:")
                if price < 20:
                    report.append("  - 低價股，流動性可能不足")
                if pe == 0:
                    report.append("  - PE 數據不足，獲利狀況待確認")
                if sm and sm > 50:
                    report.append("  - 安全邊際過高，需確認是否為價值陷阱")
                
                # 操作建議
                report.append("- 操作建議:")
                report.append(f"  - 進場: {price:.0f} 元附近")
                report.append(f"  - 停損: {price * 0.92:.0f} 元 (-8%)")
                if iv:
                    target = min(iv, price * 1.15)
                    report.append(f"  - 目標: {target:.0f} 元 (+{(target/price-1)*100:.0f}%)")
                report.append(f"  - 持股比例: 不超過總資金 10%")
                report.append("")
        
        if watch_candidates:
            report.append("### 觀察候選")
            report.append("")
            for r in watch_candidates:
                sid = r['stock_id']
                name = get_name(sid, names, r.get('name', sid))
                sm = r.get('safety_margin')
                sm_str = f"安全邊際 {sm:+.1f}%" if sm else ""
                report.append(f"- **{sid} {name}** | {r['price']:.0f} 元 | 綜合 {r['combined_score']:.0f} 分 | {sm_str}")
                report.append(f"  - 基本面低估但技術面不夠強，等突破再進")
            report.append("")
        
        if avoid_candidates:
            report.append("### 避開")
            report.append("")
            for r in avoid_candidates:
                sid = r['stock_id']
                name = get_name(sid, names, r.get('name', sid))
                report.append(f"- {sid} {name}: DCF 顯示高估")
            report.append("")
    
    # 持股追蹤
    report.append("## 持股追蹤提醒")
    report.append("")
    
    key_stocks = ['2330', '0050', '0056']
    for sid in key_stocks:
        name = get_name(sid, names, sid)
        # 從 avoids 找
        found = None
        for a in avoids:
            if a.get('stock_id') == sid:
                found = a
                break
        if found:
            report.append(f"- {sid} {name}: 評分 {found.get('score', '?')}，空頭排列，持有觀望")
        else:
            # 從 watches 找
            for w in watches:
                if w.get('stock_id') == sid:
                    report.append(f"- {sid} {name}: 評分 {w.get('score', '?')}，觀察中")
                    break
    report.append("")
    
    # 結論
    report.append("## 結論")
    report.append("")
    if bearish > total * 0.5:
        report.append("市場偏空，不宜大舉進場。持有部位設好停損，等待明確轉強訊號。")
    elif buy_candidates if dcf_results else False:
        report.append("有少數個股通過雙重驗證，可小量試單，但整體仍需謹慎。")
    else:
        report.append("目前無明確買點，繼續觀望。")
    
    report.append("")
    report.append(f"---\n*報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    # 儲存
    report_text = "\n".join(report)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    return report_text


if __name__ == "__main__":
    print(generate_report())
