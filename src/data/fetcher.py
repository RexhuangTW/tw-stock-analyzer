"""台股資料擷取器"""
import requests
import pandas as pd
from typing import Optional, List
from datetime import datetime, timedelta

from src.data.cache import cached


class TWSEFetcher:
    """台灣證券交易所資料擷取"""
    
    BASE_URL = "https://www.twse.com.tw"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        # TWSE 伺服器有時會出現 SSL 憑證問題 (Missing Subject Key Identifier)
        # 先嘗試正常驗證，失敗時自動降級為不驗證
        self._verify_ssl = True
    
    @cached(ttl_hours=24)
    def get_daily_price(self, stock_id: str, date: Optional[str] = None) -> pd.DataFrame:
        """
        取得個股日成交資訊
        
        Args:
            stock_id: 股票代號 (e.g., "2330")
            date: 日期 YYYYMMDD，預設今天
        
        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        
        url = f"{self.BASE_URL}/exchangeReport/STOCK_DAY"
        params = {
            'response': 'json',
            'date': date,
            'stockNo': stock_id
        }
        
        try:
            try:
                resp = self.session.get(url, params=params, timeout=10, verify=self._verify_ssl)
            except requests.exceptions.SSLError:
                import warnings, urllib3
                warnings.warn("TWSE SSL 憑證驗證失敗，改用不驗證模式連線", stacklevel=2)
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                self._verify_ssl = False
                resp = self.session.get(url, params=params, timeout=10, verify=False)
            resp.raise_for_status()
            data = resp.json()
            
            if data['stat'] != 'OK':
                raise ValueError(f"API 回應異常: {data.get('stat')}")
            
            # 解析資料
            df = pd.DataFrame(data['data'])
            
            # 證交所欄位: 日期、成交股數、成交金額、開盤價、最高價、最低價、收盤價、漲跌價差、成交筆數、註記
            # 對應 index: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
            df.columns = ['date', 'volume_shares', 'amount', 'open', 'high', 'low', 'close', 'change', 'transactions', 'note']
            
            # 清理資料 - 民國年轉西元年 (115 -> 2026)
            def roc_to_ad(roc_date: str) -> str:
                """民國年轉西元年 '115/03/02' -> '2026-03-02'"""
                parts = roc_date.split('/')
                if len(parts) == 3:
                    year = int(parts[0]) + 1911
                    return f"{year}-{parts[1]}-{parts[2]}"
                return roc_date
            
            df['date'] = df['date'].apply(roc_to_ad)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # 移除千分位逗號並轉數值
            for col in ['volume_shares', 'amount', 'open', 'high', 'low', 'close', 'transactions']:
                df[col] = df[col].astype(str).str.replace(',', '').astype(float, errors='ignore')
            
            # 漲跌符號處理 ('+10.00' / '-10.00' / 'X')
            df['change'] = df['change'].astype(str).str.replace('+', '').str.replace('X', '0').astype(float, errors='ignore')
            
            # 成交量轉換為張數 (1張 = 1000股)
            df['volume'] = (df['volume_shares'] / 1000).astype(int)
            
            return df[['date', 'open', 'high', 'low', 'close', 'volume', 'change', 'transactions']]
            
        except requests.RequestException as e:
            raise ConnectionError(f"無法連線到證交所: {e}")
    
    def get_historical_price(self, stock_id: str, months: int = 6) -> pd.DataFrame:
        """
        取得個股多月歷史資料
        
        Args:
            stock_id: 股票代號
            months: 往前抓幾個月
        
        Returns:
            DataFrame with historical data
        """
        from datetime import datetime, timedelta
        import time
        
        all_data = []
        current_date = datetime.now()
        
        for i in range(months):
            # 計算目標月份
            target_date = current_date - timedelta(days=30 * i)
            date_str = target_date.strftime("%Y%m%d")
            
            try:
                df = self.get_daily_price(stock_id, date_str)
                all_data.append(df)
                time.sleep(3)  # 避免被擋，每次請求間隔 3 秒
            except Exception as e:
                print(f"⚠️ 抓取 {date_str[:6]} 失敗: {e}")
                continue
        
        if not all_data:
            raise ValueError("無法取得任何歷史資料")
        
        # 合併所有月份資料並排序
        result = pd.concat(all_data, ignore_index=True)
        result = result.sort_values('date').reset_index(drop=True)
        
        return result
    
    def get_market_breadth(self, date: Optional[str] = None) -> dict:
        """
        取得大盤漲跌家數
        
        Returns:
            dict: {up: int, down: int, unchanged: int}
        """
        # TODO: 實作大盤漲跌家數擷取
        pass
    
    def get_top_movers(self, limit: int = 20) -> pd.DataFrame:
        """
        取得當日漲跌幅排行
        
        Args:
            limit: 回傳筆數
        
        Returns:
            DataFrame
        """
        # TODO: 實作漲跌排行擷取
        pass


class TPEXFetcher:
    """櫃買中心資料擷取 (上櫃股票)"""
    
    BASE_URL = "https://www.tpex.org.tw"
    
    def __init__(self):
        self.session = requests.Session()
    
    # TODO: 實作上櫃股票資料擷取
