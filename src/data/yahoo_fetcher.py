"""Yahoo Finance 資料擷取"""
import yfinance as yf
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta
from .cache import cached


class YahooFetcher:
    """Yahoo Finance 資料擷取器"""
    
    def __init__(self):
        pass
    
    @cached(ttl_hours=6)  # 6 小時快取 (盤中資料)
    def get_stock_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        取得股票資料
        
        Args:
            symbol: 股票代號 (e.g., "2330.TW", "AAPL")
            period: 時間範圍 ("1d","5d","1mo","3mo","6mo","1y","2y","5y","max")
            interval: 間隔 ("1m","2m","5m","15m","30m","60m","90m","1h","1d","5d","1wk","1mo","3mo")
        
        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            raise ValueError(f"無法取得 {symbol} 的資料")
        
        # 重設索引並重命名欄位
        df = df.reset_index()
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # 轉換成交量單位 (台股: 股 → 張)
        if symbol.endswith('.TW') or symbol.endswith('.TWO'):
            df['volume'] = (df['volume'] / 1000).astype(int)
        
        return df[['date', 'open', 'high', 'low', 'close', 'volume']]
    
    def get_info(self, symbol: str) -> dict:
        """
        取得股票基本資訊
        
        Args:
            symbol: 股票代號
        
        Returns:
            基本資訊 dict
        """
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # 提取關鍵資訊
        return {
            'symbol': symbol,
            'name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', None),
            'dividend_yield': info.get('dividendYield', None),
            'beta': info.get('beta', None),
            'year_high': info.get('fiftyTwoWeekHigh', None),
            'year_low': info.get('fiftyTwoWeekLow', None)
        }
    
    def get_realtime_price(self, symbol: str) -> dict:
        """
        取得即時報價 (延遲 15-20 分鐘)
        
        Args:
            symbol: 股票代號
        
        Returns:
            dict with price, change, change_percent
        """
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'change': info.get('regularMarketChange', 0),
            'change_percent': info.get('regularMarketChangePercent', 0),
            'volume': info.get('volume', 0),
            'timestamp': datetime.now()
        }
    
    @staticmethod
    def tw_symbol(stock_id: str, market: str = "TWSE") -> str:
        """
        轉換台股代號為 Yahoo Finance 格式
        
        Args:
            stock_id: 股票代號 (e.g., "2330")
            market: 市場 ("TWSE" 上市 / "TPEX" 上櫃)
        
        Returns:
            Yahoo Finance 代號 (e.g., "2330.TW" / "6488.TWO")
        """
        suffix = ".TW" if market == "TWSE" else ".TWO"
        return f"{stock_id}{suffix}"
