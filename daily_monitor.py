#!/usr/bin/env python3
"""每日持倉監控與警示系統 - 整合永豐 API"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import json
from datetime import datetime
from sinopac_monitor import get_quote, monitor_positions, check_entry_opportunities


def generate_daily_report():
    """產生每日監控報告"""
    print("=" * 60)
    print(f"📊 每日持倉監控報告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 持倉監控
    print("\n【持倉狀況】")
    positions_report = monitor_positions()
    
    if not positions_report:
        print("目前無持倉")
    else:
        print(positions_report)
    
    # 2. 觀察名單進場機會
    print("\n【觀察名單】")
    opportunities = check_entry_opportunities()
    
    if not opportunities:
        print("目前無進場機會")
    else:
        print(opportunities)
    
    # 3. 今日選股結果（如果有）
    picks_file = Path(__file__).parent / "today_picks.json"
    if picks_file.exists():
        print("\n【今日選股】")
        with open(picks_file, 'r') as f:
            picks = json.load(f)
        
        if 'swing' in picks:
            swing_buys = picks['swing'].get('buys', [])
            if swing_buys:
                print(f"短線候選 {len(swing_buys)} 檔:")
                for stock in swing_buys[:5]:
                    print(f"  {stock['stock_id']}: {stock.get('current_price', 'N/A')}元 評分{stock['score']:.1f}")
        
        if 'invest' in picks:
            invest_buys = picks['invest'].get('buys', [])
            if invest_buys:
                print(f"\n投資候選 {len(invest_buys)} 檔:")
                for stock in invest_buys[:3]:
                    print(f"  {stock['stock_id']}: {stock.get('current_price', 'N/A')}元 DCF{stock.get('dcf_value', 'N/A')}")
    
    print("\n" + "=" * 60)


def check_alerts():
    """檢查警示條件（停損/停利/進場機會）"""
    alerts = []
    
    # 查詢持倉
    from sinopac_config import SINOPAC_CONFIG, check_config
    if not check_config():
        return alerts
    
    import shioaji as sj
    api = sj.Shioaji(simulation=False)
    
    try:
        api.login(
            api_key=SINOPAC_CONFIG['api_key'],
            secret_key=SINOPAC_CONFIG['secret_key']
        )
        
        # 查詢持倉（含零股）
        positions = api.list_positions(
            api.stock_account,
            unit=sj.constant.Unit.Share
        )
        
        for pos in positions:
            shares = int(pos.quantity)
            if shares == 0:
                continue
            
            code = pos.code
            quote = get_quote(api, code)
            if not quote:
                continue
            
            current = quote['price']
            cost = float(pos.price)
            pnl_pct = (current - cost) / cost * 100
            
            # 停損警示（-5%）
            if pnl_pct <= -5:
                alerts.append({
                    'type': 'STOP_LOSS',
                    'code': code,
                    'current': current,
                    'cost': cost,
                    'pnl_pct': pnl_pct,
                    'message': f"🚨 {code} 觸發停損！現價{current} 成本{cost} ({pnl_pct:+.2f}%)"
                })
            
            # 停利警示（+10% 或 +15%）
            elif pnl_pct >= 15:
                alerts.append({
                    'type': 'TAKE_PROFIT_FULL',
                    'code': code,
                    'current': current,
                    'cost': cost,
                    'pnl_pct': pnl_pct,
                    'message': f"💰 {code} 達到目標價！現價{current} 成本{cost} ({pnl_pct:+.2f}%) - 建議全清"
                })
            
            elif pnl_pct >= 10:
                alerts.append({
                    'type': 'TAKE_PROFIT_HALF',
                    'code': code,
                    'current': current,
                    'cost': cost,
                    'pnl_pct': pnl_pct,
                    'message': f"💰 {code} 達到停利點！現價{current} 成本{cost} ({pnl_pct:+.2f}%) - 建議賣一半"
                })
        
        # 檢查觀察名單進場機會
        watches_file = Path(__file__).parent / "today_picks.json"
        if watches_file.exists():
            with open(watches_file, 'r') as f:
                picks = json.load(f)
            
            watches = picks.get('swing', {}).get('watches', [])
            for stock in watches[:10]:  # 檢查前 10 檔
                code = stock['stock_id']
                entry_price = stock.get('entry_price', 0)
                
                if entry_price > 0:
                    quote = get_quote(api, code)
                    if quote:
                        current = quote['price']
                        diff_pct = (current - entry_price) / entry_price * 100
                        
                        # 接近進場價（±2%）
                        if -2 <= diff_pct <= 2:
                            alerts.append({
                                'type': 'ENTRY_OPPORTUNITY',
                                'code': code,
                                'current': current,
                                'entry_price': entry_price,
                                'diff_pct': diff_pct,
                                'message': f"👀 {code} 接近進場價！現價{current} 進場{entry_price} ({diff_pct:+.2f}%)"
                            })
        
        api.logout()
        
    except Exception as e:
        print(f"警示檢查失敗: {e}")
    
    return alerts


def send_alerts(alerts):
    """發送警示（Discord 通知）"""
    if not alerts:
        return
    
    message = "🔔 **即時警示**\n\n"
    for alert in alerts:
        message += alert['message'] + "\n"
    
    print(message)
    # TODO: 整合 Discord webhook


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='每日持倉監控')
    parser.add_argument('--check-alerts', action='store_true', help='檢查並發送警示')
    parser.add_argument('--report', action='store_true', help='產生每日報告')
    args = parser.parse_args()
    
    if args.check_alerts:
        alerts = check_alerts()
        if alerts:
            send_alerts(alerts)
        else:
            print("✅ 無警示事項")
    elif args.report:
        generate_daily_report()
    else:
        # 預設：產生報告
        generate_daily_report()
