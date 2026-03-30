#!/usr/bin/env python3
"""
永豐金即時看盤與監控
功能：
1. 即時報價查詢
2. 持倉監控（技術面警示）
3. 觀察名單進場提醒
"""

import shioaji as sj
from datetime import datetime
import json
from pathlib import Path
from sinopac_config import SINOPAC_CONFIG, check_config

class SinopacMonitor:
    """永豐金即時監控"""
    
    def __init__(self):
        self.api = None
        self.connected = False
        
    def connect(self):
        """連線到永豐 API"""
        if not check_config():
            return False
            
        try:
            self.api = sj.Shioaji()
            
            # 登入
            self.api.login(
                api_key=SINOPAC_CONFIG['api_key'],
                secret_key=SINOPAC_CONFIG['secret_key'],
                contracts_cb=lambda security_type: print(f"✅ 載入合約: {security_type}")
            )
            
            print("✅ 永豐 API 連線成功")
            self.connected = True
            return True
            
        except Exception as e:
            print(f"❌ 連線失敗: {e}")
            return False
    
    def get_quote(self, code):
        """取得即時報價"""
        if not self.connected:
            print("❌ 未連線")
            return None
            
        try:
            contract = self.api.Contracts.Stocks[code]
            snapshot = self.api.snapshots([contract])[0]
            
            # 計算漲跌幅
            try:
                change_pct = (snapshot.close - snapshot.open) / snapshot.open * 100
            except:
                change_pct = 0
            
            return {
                'code': code,
                'name': contract.name,
                'price': snapshot.close,
                'open': snapshot.open,
                'high': snapshot.high,
                'low': snapshot.low,
                'volume': snapshot.volume,
                'change_pct': change_pct,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"❌ 取得報價失敗 ({code}): {e}")
            return None
    
    def monitor_portfolio(self):
        """監控持倉（從永豐證券帳戶查詢）"""
        print("=" * 60)
        print(f"📦 持倉監控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # 查詢證券帳戶實際持倉（以「股」為單位，包含零股）
            positions = self.api.list_positions(
                self.api.stock_account,
                unit=sj.constant.Unit.Share  # 改為股數單位
            )
            
            if not positions:
                print("目前無持倉")
                return
            
            for pos in positions:
                code = pos.code
                shares = int(pos.quantity)  # 股數（unit=Share 時回傳股數）
                
                # 跳過已清倉的部位
                if shares == 0:
                    continue
                    
                lots = shares / 1000  # 張數
                
                # 取得即時報價
                quote = self.get_quote(code)
                if not quote:
                    continue
                
                current = quote['price']
                cost = float(pos.price)  # 成本價
                pnl = float(pos.pnl)  # 損益
                pnl_pct = (current - cost) / cost * 100
                market_value = current * shares
                
                print(f"\n{code} {quote['name']}")
                if lots >= 1:
                    print(f"  持有: {lots:.0f} 張 ({shares:,} 股)")
                else:
                    print(f"  持有: {shares:,} 股（零股）")
                print(f"  成本: {cost:.2f} 元")
                print(f"  現價: {current:.2f} 元 ({quote['time']})")
                print(f"  損益: {pnl:+,.0f} 元 ({pnl_pct:+.2f}%)")
                print(f"  市值: {market_value:,.0f} 元")
                
                # 技術面警示
                stop_loss = cost * 0.95  # -5%
                target = cost * 1.15  # +15%
                
                if current <= stop_loss:
                    print(f"  🚨 觸發停損 ({stop_loss:.2f}) - 建議立即出場")
                elif current >= target * 0.8:
                    print(f"  💰 接近目標 ({target:.2f}) - 考慮停利")
                else:
                    print(f"  📊 正常持有")
                    
        except Exception as e:
            print(f"❌ 查詢持倉失敗: {e}")
            print("（可能是未登入證券帳戶或無部位）")
    
    def monitor_watchlist(self):
        """監控觀察名單"""
        portfolio_file = Path(__file__).parent / "portfolio.json"
        
        if not portfolio_file.exists():
            return
            
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        
        print()
        print("=" * 60)
        print("👀 觀察名單 - 進場機會")
        print("=" * 60)
        
        if not portfolio['watchlist']:
            print("目前無觀察標的")
            return
        
        signals = []
        
        for watch in portfolio['watchlist']:
            quote = self.get_quote(watch['code'])
            if not quote:
                continue
            
            current = quote['price']
            entry = watch['entry_price']
            diff_pct = (current - entry) / entry * 100
            
            if abs(diff_pct) <= 2:
                signals.append({
                    'code': watch['code'],
                    'name': quote['name'],
                    'current': current,
                    'entry': entry,
                    'diff_pct': diff_pct,
                    'action': '✅ 可進場'
                })
        
        if signals:
            for sig in signals:
                print(f"\n{sig['action']} {sig['code']} {sig['name']}")
                print(f"  當前: {sig['current']:.2f} 元")
                print(f"  進場: {sig['entry']:.2f} 元")
                print(f"  差距: {sig['diff_pct']:+.1f}%")
        else:
            print("目前無適合進場標的")
    
    def disconnect(self):
        """斷線"""
        if self.api:
            self.api.logout()
            print("✅ 已登出")

def main():
    """主程式"""
    monitor = SinopacMonitor()
    
    if not monitor.connect():
        return
    
    try:
        # 監控持倉
        monitor.monitor_portfolio()
        
        # 監控觀察名單
        monitor.monitor_watchlist()
        
    finally:
        monitor.disconnect()

def get_quote(api, code):
    """查詢單一股票即時報價（供外部呼叫）"""
    try:
        contract = api.Contracts.Stocks[code]
        snapshots = api.snapshots([contract])
        if snapshots:
            snap = snapshots[0]
            return {
                'code': code,
                'name': contract.name,
                'price': snap.close,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    except:
        pass
    return None


def monitor_positions():
    """監控持倉（返回文字報告，供外部呼叫）"""
    from sinopac_config import SINOPAC_CONFIG, check_config
    if not check_config():
        return "永豐 API 設定不完整"
    
    import shioaji as sj
    api = sj.Shioaji(simulation=False)
    
    try:
        api.login(
            api_key=SINOPAC_CONFIG['api_key'],
            secret_key=SINOPAC_CONFIG['secret_key']
        )
        
        positions = api.list_positions(
            api.stock_account,
            unit=sj.constant.Unit.Share
        )
        
        report = []
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
            lots = shares / 1000
            
            if lots >= 1:
                report.append(f"{code} {quote['name']}: {lots:.0f}張 現價{current} 成本{cost} ({pnl_pct:+.2f}%)")
            else:
                report.append(f"{code} {quote['name']}: {shares}股 現價{current} 成本{cost} ({pnl_pct:+.2f}%)")
        
        api.logout()
        return "\n".join(report) if report else "無持倉"
        
    except Exception as e:
        return f"查詢失敗: {e}"


def check_entry_opportunities():
    """檢查觀察名單進場機會（供外部呼叫）"""
    # 讀取今日選股結果
    import json
    picks_file = Path(__file__).parent / "today_picks.json"
    if not picks_file.exists():
        return "無觀察名單"
    
    with open(picks_file, 'r') as f:
        picks = json.load(f)
    
    watches = picks.get('swing', {}).get('watches', [])
    if not watches:
        return "無觀察名單"
    
    from sinopac_config import SINOPAC_CONFIG, check_config
    if not check_config():
        return "永豐 API 設定不完整"
    
    import shioaji as sj
    api = sj.Shioaji(simulation=False)
    
    try:
        api.login(
            api_key=SINOPAC_CONFIG['api_key'],
            secret_key=SINOPAC_CONFIG['secret_key']
        )
        
        opportunities = []
        for stock in watches[:10]:
            code = stock['stock_id']
            entry_price = stock.get('entry_price', 0)
            
            if entry_price > 0:
                quote = get_quote(api, code)
                if quote:
                    current = quote['price']
                    diff_pct = (current - entry_price) / entry_price * 100
                    
                    if abs(diff_pct) <= 2:
                        opportunities.append(f"{code}: 現價{current} 進場{entry_price} ({diff_pct:+.2f}%)")
        
        api.logout()
        return "\n".join(opportunities) if opportunities else "無進場機會"
        
    except Exception as e:
        return f"查詢失敗: {e}"


if __name__ == '__main__':
    main()
