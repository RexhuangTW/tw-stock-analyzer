"""股票監控器"""
import time
from datetime import datetime
from typing import List, Dict, Callable, Optional
import pandas as pd
from src.data.fetcher import TWSEFetcher
from src.indicators.technical import calculate_rsi, calculate_ma


class StockWatcher:
    """即時股票監控"""
    
    def __init__(self, check_interval: int = 300):
        """
        Args:
            check_interval: 檢查間隔 (秒)，預設 5 分鐘
        """
        self.fetcher = TWSEFetcher()
        self.check_interval = check_interval
        self.watchlist: Dict[str, Dict] = {}
        self.alert_handlers: List[Callable] = []
    
    def add_stock(self, 
                  stock_id: str, 
                  conditions: Optional[Dict] = None) -> 'StockWatcher':
        """
        加入監控股票
        
        Args:
            stock_id: 股票代號
            conditions: 觸發條件，例如 {'price_above': 100, 'rsi_below': 30}
        
        Returns:
            self (支援鏈式呼叫)
        """
        self.watchlist[stock_id] = {
            'conditions': conditions or {},
            'last_check': None,
            'last_price': None
        }
        print(f"➕ 加入監控: {stock_id}")
        return self
    
    def remove_stock(self, stock_id: str) -> 'StockWatcher':
        """移除監控股票"""
        if stock_id in self.watchlist:
            del self.watchlist[stock_id]
            print(f"➖ 移除監控: {stock_id}")
        return self
    
    def add_alert_handler(self, handler: Callable) -> 'StockWatcher':
        """
        新增警報處理器
        
        Args:
            handler: 接受 (stock_id, alert_msg) 的函數
        """
        self.alert_handlers.append(handler)
        return self
    
    def _check_conditions(self, stock_id: str, data: pd.Series, conditions: Dict) -> List[str]:
        """
        檢查觸發條件
        
        Returns:
            觸發的警報訊息列表
        """
        alerts = []
        
        if 'price_above' in conditions and data['close'] > conditions['price_above']:
            alerts.append(f"股價突破 {conditions['price_above']}")
        
        if 'price_below' in conditions and data['close'] < conditions['price_below']:
            alerts.append(f"股價跌破 {conditions['price_below']}")
        
        if 'rsi_above' in conditions and 'rsi' in data and data['rsi'] > conditions['rsi_above']:
            alerts.append(f"RSI 突破 {conditions['rsi_above']} (當前: {data['rsi']:.1f})")
        
        if 'rsi_below' in conditions and 'rsi' in data and data['rsi'] < conditions['rsi_below']:
            alerts.append(f"RSI 跌破 {conditions['rsi_below']} (當前: {data['rsi']:.1f})")
        
        if 'volume_above' in conditions and data['volume'] > conditions['volume_above']:
            alerts.append(f"成交量放大至 {data['volume']} 張")
        
        return alerts
    
    def check_once(self) -> Dict[str, List[str]]:
        """
        執行一次檢查
        
        Returns:
            {stock_id: [alerts]}
        """
        all_alerts = {}
        
        for stock_id, info in self.watchlist.items():
            try:
                # 取得最新資料
                df = self.fetcher.get_historical_price(stock_id, months=1)
                
                # 計算指標
                df['rsi'] = calculate_rsi(df['close'], period=14)
                df['ma5'] = calculate_ma(df['close'], 5)
                
                latest = df.iloc[-1]
                
                # 檢查條件
                alerts = self._check_conditions(stock_id, latest, info['conditions'])
                
                if alerts:
                    all_alerts[stock_id] = alerts
                    
                    # 呼叫警報處理器
                    for handler in self.alert_handlers:
                        for alert in alerts:
                            handler(stock_id, alert)
                
                # 更新狀態
                info['last_check'] = datetime.now()
                info['last_price'] = latest['close']
                
            except Exception as e:
                print(f"⚠️ {stock_id} 檢查失敗: {e}")
                continue
        
        return all_alerts
    
    def start_monitoring(self, max_iterations: Optional[int] = None):
        """
        開始持續監控
        
        Args:
            max_iterations: 最大迭代次數 (None = 無限)
        """
        print(f"🚀 開始監控 {len(self.watchlist)} 支股票 (每 {self.check_interval} 秒)")
        
        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            print(f"\n⏰ [{datetime.now().strftime('%H:%M:%S')}] 執行檢查...")
            
            alerts = self.check_once()
            
            if alerts:
                print(f"🚨 發現 {len(alerts)} 筆警報")
                for stock_id, msgs in alerts.items():
                    for msg in msgs:
                        print(f"  • {stock_id}: {msg}")
            else:
                print("✅ 無警報")
            
            iteration += 1
            
            if max_iterations is None or iteration < max_iterations:
                print(f"💤 等待 {self.check_interval} 秒...")
                time.sleep(self.check_interval)
        
        print("🛑 監控結束")


# 內建警報處理器

def console_alert_handler(stock_id: str, message: str):
    """輸出到 console"""
    print(f"🔔 [{datetime.now().strftime('%H:%M:%S')}] {stock_id}: {message}")


def file_alert_handler(log_path: str):
    """寫入檔案"""
    def handler(stock_id: str, message: str):
        with open(log_path, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {stock_id}: {message}\n")
    return handler
