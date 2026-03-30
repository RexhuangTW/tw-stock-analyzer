#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""選股報告生成器 - 支援雙策略報告"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
NAMES_FILE = BASE_DIR / "stock_names.json"
PICKS_FILE = BASE_DIR / "today_picks.json"
REPORT_FILE = BASE_DIR / "daily_report.md"
SWING_REPORT_FILE = BASE_DIR / "swing_report.md"
INVEST_REPORT_FILE = BASE_DIR / "invest_report.md"


def load_names():
    if NAMES_FILE.exists():
        with open(NAMES_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_name(stock_id, names, fallback=""):
    return names.get(stock_id, fallback)


# ==================== 短線報告 ====================

def generate_swing_report(swing_data, date, names):
    """產生短線操作報告"""
    lines = []
    lines.append(f"# 短線操作候選（{date}）")
    lines.append("")
    lines.append("---")
    lines.append("")

    buys = swing_data.get('buys', [])
    watches = swing_data.get('watches', [])
    total = swing_data.get('total_analyzed', 0)

    lines.append(f"分析標的: {total} 檔 | 強勢候選: {len(buys)} 檔 | 觀察: {len(watches)} 檔")
    lines.append("")

    if buys:
        lines.append("## 強勢突破")
        lines.append("")
        for i, r in enumerate(buys, 1):
            sid = r['stock_id']
            name = get_name(sid, names, sid)
            lines.append(f"{i}. **{sid} {name}** | {r['close']:.0f} 元 | 評分 {r['score']}")
            if r.get('change_pct'):
                lines.append(f"   - 今日 {r['change_pct']:+.2f}%，{r['ma_trend']}")
            lines.append(f"   - 進場：{r.get('entry', '-')} (回檔買)")
            lines.append(f"   - 停損：{r.get('stop_loss', '-')} ({r.get('stop_loss_pct', '')})")
            lines.append(f"   - 目標：{r.get('target', '-')} ({r.get('target_pct', '')})")
            lines.append(f"   - 持有：{r.get('hold_period', '1-2 週')}")
            lines.append("")
    else:
        lines.append("## 無強勢候選")
        lines.append("")

    if watches:
        lines.append("## 觀察名單")
        lines.append("")
        for r in watches:
            sid = r['stock_id']
            name = get_name(sid, names, sid)
            lines.append(f"- **{sid} {name}** | {r['close']:.0f} 元 | 評分 {r['score']} | RSI {r['rsi']} | {r['ma_trend']}")
        lines.append("")

    avoids = swing_data.get('avoids', [])
    if avoids:
        lines.append("## 避開")
        lines.append("")
        for r in avoids[:5]:
            sid = r['stock_id']
            name = get_name(sid, names, sid)
            lines.append(f"- {sid} {name}: 評分 {r['score']}")
        lines.append("")

    lines.append(f"---\n*報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    return "\n".join(lines)


# ==================== 投資報告 ====================

def generate_invest_report(invest_data, date, names):
    """產生投資佈局報告"""
    lines = []
    lines.append(f"# 投資佈局候選（{date}）")
    lines.append("")
    lines.append("---")
    lines.append("")

    buys = invest_data.get('buys', [])
    watches = invest_data.get('watches', [])
    total = invest_data.get('total_analyzed', 0)

    lines.append(f"分析標的: {total} 檔 | 價值低估: {len(buys)} 檔 | 觀察佈局: {len(watches)} 檔")
    lines.append("")

    if buys:
        lines.append("## 價值低估")
        lines.append("")
        for i, r in enumerate(buys, 1):
            sid = r['stock_id']
            name = get_name(sid, names, r.get('name', sid))
            lines.append(f"{i}. **{sid} {name}** | 評分 {r['score']}")

            iv = r.get('intrinsic_value')
            sm = r.get('safety_margin')
            if iv:
                lines.append(f"   - DCF 內在價值：{iv:.0f} 元")
            lines.append(f"   - 當前價格：{r['close']:.0f} 元")
            if sm is not None:
                lines.append(f"   - 安全邊際：{sm:+.1f}%")
            if r.get('expected_return'):
                lines.append(f"   - 預期報酬：{r['expected_return']}")

            # 基本面細節
            pe = r.get('pe')
            if pe:
                try:
                    pe_val = float(pe)
                    if pe_val > 0:
                        lines.append(f"   - PE：{pe_val:.1f}x")
                except (ValueError, TypeError):
                    pass
            
            dy = r.get('dividend_yield')
            if dy:
                try:
                    dy_val = float(dy)
                    if dy_val > 0:
                        lines.append(f"   - 殖利率：{dy_val:.1f}%")
                except (ValueError, TypeError):
                    pass
            if r.get('revenue_growth'):
                lines.append(f"   - 營收成長：{r['revenue_growth']:+.1f}%")
            if r.get('sector'):
                lines.append(f"   - 產業：{r['sector']}")

            lines.append(f"   - 停損：{r.get('stop_loss', '-')} ({r.get('stop_loss_pct', '')})")
            lines.append(f"   - 建議：{r.get('action', '分批布局')}")
            lines.append(f"   - 持有：{r.get('hold_period', '3-6 月')}")
            lines.append("")
    else:
        lines.append("## 無價值低估標的")
        lines.append("")

    if watches:
        lines.append("## 觀察佈局")
        lines.append("")
        for r in watches:
            sid = r['stock_id']
            name = get_name(sid, names, r.get('name', sid))
            sm = f"安全邊際 {r['safety_margin']:+.1f}%" if r.get('safety_margin') is not None else ""
            lines.append(f"- **{sid} {name}** | {r['close']:.0f} 元 | 評分 {r['score']} | {sm}")
        lines.append("")

    lines.append(f"---\n*報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    return "\n".join(lines)


# ==================== 雙策略報告 ====================

def generate_dual_report(output=None):
    """生成雙策略選股報告"""
    if output is None:
        if not PICKS_FILE.exists():
            return "無選股資料"
        with open(PICKS_FILE) as f:
            output = json.load(f)

    names = load_names()
    date = output.get('date', datetime.now().strftime('%Y-%m-%d'))

    reports_generated = []

    # 短線報告
    swing_data = output.get('swing')
    if swing_data:
        swing_text = generate_swing_report(swing_data, date, names)
        with open(SWING_REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(swing_text)
        reports_generated.append(str(SWING_REPORT_FILE))

    # 投資報告
    invest_data = output.get('invest')
    if invest_data:
        invest_text = generate_invest_report(invest_data, date, names)
        with open(INVEST_REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(invest_text)
        reports_generated.append(str(INVEST_REPORT_FILE))

    # 合併日報
    combined = []
    combined.append(f"# 每日選股報告（{date}）")
    combined.append("")
    combined.append("---")
    combined.append("")

    if swing_data and invest_data:
        swing_buys = len(swing_data.get('buys', []))
        invest_buys = len(invest_data.get('buys', []))
        combined.append("## 總覽")
        combined.append("")
        combined.append(f"| 策略 | 候選數 | 觀察數 |")
        combined.append(f"|------|--------|--------|")
        combined.append(f"| 短線操作 | {swing_buys} | {len(swing_data.get('watches', []))} |")
        combined.append(f"| 投資佈局 | {invest_buys} | {len(invest_data.get('watches', []))} |")
        combined.append("")

    if swing_data:
        combined.append(generate_swing_report(swing_data, date, names))
        combined.append("")

    if invest_data:
        combined.append(generate_invest_report(invest_data, date, names))

    combined_text = "\n".join(combined)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(combined_text)
    reports_generated.append(str(REPORT_FILE))

    return reports_generated


# ==================== 舊版相容 ====================

def generate_report():
    """向下相容：如果 today_picks.json 是舊格式就走舊邏輯，新格式走雙策略"""
    if not PICKS_FILE.exists():
        return "無選股資料"
    with open(PICKS_FILE) as f:
        picks = json.load(f)

    # 新格式含 swing / invest key
    if 'swing' in picks or 'invest' in picks:
        return generate_dual_report(picks)

    # ---------- 舊格式相容 ----------
    names = load_names()
    date = picks.get('date', datetime.now().strftime('%Y-%m-%d'))
    total = picks.get('total_analyzed', 0)
    buys = picks.get('buys', [])
    watches = picks.get('watches', [])
    avoids = picks.get('avoids', [])
    dcf_results = picks.get('dcf_results', [])

    bullish = len([w for w in watches if w.get('ma_trend') == '多頭'])
    bearish = len(avoids)

    report = []
    report.append(f"# 每日選股報告 ({date})")
    report.append("")
    report.append("---")
    report.append("")
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
                if sector:
                    report.append(f"- 產業: {sector}")
                report.append("- 選中原因:")
                if sm and sm > 0:
                    report.append(f"  - DCF 內在價值 {iv:.0f} 元，目前 {price:.0f} 元被低估 {sm:.0f}%")
                tech_score = r.get('tech_score', 0)
                if tech_score >= 60:
                    report.append(f"  - 技術面評分 {tech_score:.0f}，均線多頭排列")
                if pe > 0 and pe < 15:
                    report.append(f"  - PE {pe:.1f}x 偏低，估值合理")
                if 1 < dy < 15:
                    report.append(f"  - 殖利率 {dy:.1f}%，有股息保護")
                if rg > 10:
                    report.append(f"  - 營收成長 {rg:.1f}%，成長動能佳")
                report.append("- 風險:")
                if price < 20:
                    report.append("  - 低價股，流動性可能不足")
                if pe == 0:
                    report.append("  - PE 數據不足，獲利狀況待確認")
                if sm and sm > 50:
                    report.append("  - 安全邊際過高，需確認是否為價值陷阱")
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

    report.append("## 結論")
    report.append("")
    if bearish > total * 0.5:
        report.append("市場偏空，不宜大舉進場。持有部位設好停損，等待明確轉強訊號。")
    elif dcf_results and any('買進' in r.get('recommendation', '') for r in dcf_results):
        report.append("有少數個股通過雙重驗證，可小量試單，但整體仍需謹慎。")
    else:
        report.append("目前無明確買點，繼續觀望。")

    report.append("")
    report.append(f"---\n*報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    report_text = "\n".join(report)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_text)

    return report_text


if __name__ == "__main__":
    result = generate_report()
    if isinstance(result, list):
        print(f"報告已生成: {', '.join(result)}")
    else:
        print(result)
