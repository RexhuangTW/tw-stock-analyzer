#!/usr/bin/env python3
"""
持倉監控腳本
每日檢查觀察名單和持倉狀態
"""

import json
import yfinance as yf
from datetime import datetime
from pathlib import Path

def load_portfolio():
    """載入持倉資料"""
    portfolio_file = Path(__file__).parent / "portfolio.json"
    with open(portfolio_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_portfolio(portfolio):
    """儲存持倉資料"""
    portfolio_file = Path(__file__).parent / "portfolio.json"
    portfolio['updated_at'] = datetime.now().strftime('%Y-%m-%d')
    with open(portfolio_file, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)

def get_current_price(code):
    """取得當前價格"""
    try:
        ticker = yf.Ticker(f"{code}.TW")
        data = ticker.history(period='1d')
        if not data.empty:
            return float(data['Close'].iloc[-1])
    except:
        pass
    return None

def check_entry_signals(portfolio):
    """檢查進場訊號"""
    signals = []
    
    for watch in portfolio['watchlist']:
        if watch['status'] != 'watching':
            continue
            
        current = get_current_price(watch['code'])
        if current is None:
            continue
            
        watch['current_price'] = current
        entry = watch['entry_price']
        
        # 檢查是否達到進場價 (±2%)
        diff_pct = (current - entry) / entry * 100
        
        if abs(diff_pct) <= 2:
            signals.append({
                'code': watch['code'],
                'name': watch['name'],
                'current': current,
                'entry': entry,
                'diff_pct': diff_pct,
                'action': '✅ 可進場',
                'reason': f"當前 {current} 元，接近進場價 {entry} 元 ({diff_pct:+.1f}%)"
            })
        elif diff_pct < -2:
            signals.append({
                'code': watch['code'],
                'name': watch['name'],
                'current': current,
                'entry': entry,
                'diff_pct': diff_pct,
                'action': '🎯 更好價位',
                'reason': f"當前 {current} 元，低於進場價 {entry} 元 ({diff_pct:+.1f}%)，可考慮提前布局"
            })
    
    save_portfolio(portfolio)
    return signals

def check_positions(portfolio):
    """檢查持倉狀態"""
    alerts = []
    
    for pos in portfolio['positions']:
        if pos['status'] != 'holding':
            continue
            
        current = get_current_price(pos['code'])
        if current is None:
            continue
            
        buy_price = pos['buy_price']
        stop_loss = pos['stop_loss']
        target = pos['target']
        
        profit_pct = (current - buy_price) / buy_price * 100
        cost = pos['shares'] * buy_price
        value = pos['shares'] * current
        profit = value - cost
        
        # 檢查停損
        if current <= stop_loss:
            alerts.append({
                'type': '🚨 停損警示',
                'code': pos['code'],
                'name': pos['name'],
                'current': current,
                'buy_price': buy_price,
                'stop_loss': stop_loss,
                'profit_pct': profit_pct,
                'profit': profit,
                'action': '立即出場'
            })
        # 檢查達標
        elif current >= target * 0.8:  # 達到目標 80%
            alerts.append({
                'type': '💰 停利提醒',
                'code': pos['code'],
                'name': pos['name'],
                'current': current,
                'buy_price': buy_price,
                'target': target,
                'profit_pct': profit_pct,
                'profit': profit,
                'action': f"已達標 {profit_pct:.1f}%，考慮分批出場"
            })
        # 正常持有
        else:
            alerts.append({
                'type': '📊 持倉狀態',
                'code': pos['code'],
                'name': pos['name'],
                'current': current,
                'buy_price': buy_price,
                'profit_pct': profit_pct,
                'profit': profit,
                'action': '持續觀察'
            })
    
    save_portfolio(portfolio)
    return alerts

def generate_report():
    """生成每日報告"""
    portfolio = load_portfolio()
    
    print("=" * 60)
    print(f"📊 持倉監控報告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()
    
    # 資金狀況
    total_value = portfolio['cash']
    for pos in portfolio['positions']:
        if pos['status'] == 'holding':
            current = get_current_price(pos['code'])
            if current:
                total_value += pos['shares'] * current
    
    print(f"💰 總資產: {total_value:,.0f} 元")
    print(f"💵 現金: {portfolio['cash']:,.0f} 元")
    print(f"📈 持倉: {total_value - portfolio['cash']:,.0f} 元")
    print(f"🎯 總報酬: {(total_value - portfolio['initial_capital']) / portfolio['initial_capital'] * 100:+.2f}%")
    print()
    
    # 持倉檢查
    if portfolio['positions']:
        print("=" * 60)
        print("📦 持倉檢查")
        print("=" * 60)
        alerts = check_positions(portfolio)
        for alert in alerts:
            print(f"\n{alert['type']}")
            print(f"  {alert['code']} {alert['name']}")
            print(f"  買進: {alert['buy_price']:.2f} 元")
            print(f"  現價: {alert['current']:.2f} 元")
            print(f"  損益: {alert['profit']:+,.0f} 元 ({alert['profit_pct']:+.2f}%)")
            print(f"  建議: {alert['action']}")
    else:
        print("📦 目前無持倉")
    
    print()
    
    # 觀察名單檢查
    print("=" * 60)
    print("👀 觀察名單 - 進場機會")
    print("=" * 60)
    signals = check_entry_signals(portfolio)
    
    if signals:
        for sig in signals:
            print(f"\n{sig['action']} {sig['code']} {sig['name']}")
            print(f"  {sig['reason']}")
    else:
        print("目前無適合進場標的，建議繼續觀察")
    
    print()
    print("=" * 60)

if __name__ == '__main__':
    generate_report()

def check_technical_signals(portfolio):
    """檢查技術面訊號（比停損更早）"""
    warnings = []
    
    for pos in portfolio['positions']:
        if pos['status'] != 'holding':
            continue
            
        code = pos['code']
        
        # 取得技術指標
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{code}.TW")
            data = ticker.history(period='60d')
            
            if len(data) < 20:
                continue
                
            # 計算 MA
            data['ma5'] = data['Close'].rolling(5).mean()
            data['ma10'] = data['Close'].rolling(10).mean()
            data['ma20'] = data['Close'].rolling(20).mean()
            
            latest = data.iloc[-1]
            current = latest['Close']
            
            # 檢查 MA 破位
            if current < latest['ma10']:
                warnings.append({
                    'level': '🚨 緊急',
                    'code': code,
                    'name': pos['name'],
                    'signal': '跌破 MA10',
                    'current': current,
                    'ma10': latest['ma10'],
                    'action': '建議立即出場（不等停損）',
                    'reason': '短線趨勢轉弱'
                })
            elif current < latest['ma5']:
                warnings.append({
                    'level': '⚠️ 警示',
                    'code': code,
                    'name': pos['name'],
                    'signal': '跌破 MA5',
                    'current': current,
                    'ma5': latest['ma5'],
                    'action': '明天再觀察，持續破線就出場',
                    'reason': '可能轉弱'
                })
        except:
            pass
    
    return warnings
