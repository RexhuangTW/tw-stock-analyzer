#!/usr/bin/env python3
"""
永豐金 API 資料抓取器
- 批次查詢即時報價
- 支援歷史資料（K線）
- 取代 yahoo_fetcher.py
"""

import shioaji as sj
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
from pathlib import Path
import sys

# 加入專案根目錄到 path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from sinopac_config import SINOPAC_CONFIG, check_config


class SinopacFetcher:
    """永豐金 API 資料抓取器"""
    
    def __init__(self):
        """初始化 API 連線"""
        if not check_config():
            raise ValueError("永豐 API 設定不完整")
        
        self.api = sj.Shioaji(simulation=False)
        self._is_logged_in = False
    
    def login(self):
        """登入 API"""
        if self._is_logged_in:
            return
        
        try:
            self.api.login(
                api_key=SINOPAC_CONFIG['api_key'],
                secret_key=SINOPAC_CONFIG['secret_key']
            )
            self._is_logged_in = True
            print("✅ 永豐 API 登入成功")
        except Exception as e:
            print(f"❌ 永豐 API 登入失敗: {e}")
            raise
    
    def logout(self):
        """登出 API"""
        if self._is_logged_in:
            self.api.logout()
            self._is_logged_in = False
            print("✅ 已登出")
    
    def __enter__(self):
        """Context manager - 進入"""
        self.login()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - 離開"""
        self.logout()
    
    def get_snapshot(self, codes: List[str]) -> pd.DataFrame:
        """
        批次查詢即時快照
        
        Args:
            codes: 股票代碼列表（最多 500 檔）
        
        Returns:
            DataFrame with columns: code, close, open, high, low, volume, 
                                   change_price, change_rate, ts
        """
        if not self._is_logged_in:
            self.login()
        
        if len(codes) > 500:
            raise ValueError("單次查詢最多 500 檔")
        
        # 建立合約列表
        contracts = []
        for code in codes:
            try:
                contract = self.api.Contracts.Stocks[code]
                contracts.append(contract)
            except KeyError:
                print(f"⚠️ 股票代碼 {code} 不存在，跳過")
                continue
        
        if not contracts:
            return pd.DataFrame()
        
        # 批次查詢
        snapshots = self.api.snapshots(contracts)
        
        # 轉換為 DataFrame
        data = []
        for snap in snapshots:
            data.append({
                'code': snap.code,
                'close': snap.close,
                'open': snap.open,
                'high': snap.high,
                'low': snap.low,
                'volume': snap.total_volume,
                'change_price': snap.change_price,
                'change_rate': snap.change_rate,
                'ts': pd.to_datetime(snap.ts, unit='s')
            })
        
        df = pd.DataFrame(data)
        return df
    
    def get_historical_data(
        self, 
        code: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = '60d'
    ) -> pd.DataFrame:
        """
        查詢歷史 K 線資料
        
        Args:
            code: 股票代碼
            start_date: 開始日期 (YYYY-MM-DD)，優先於 period
            end_date: 結束日期 (YYYY-MM-DD)
            period: 查詢期間（60d, 3mo, 6mo, 1y）
        
        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        if not self._is_logged_in:
            self.login()
        
        try:
            contract = self.api.Contracts.Stocks[code]
        except KeyError:
            raise ValueError(f"股票代碼 {code} 不存在")
        
        # 計算日期範圍
        if end_date is None:
            end = datetime.now()
        else:
            end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            # 解析 period
            if period.endswith('d'):
                days = int(period[:-1])
                start = end - timedelta(days=days)
            elif period.endswith('mo'):
                months = int(period[:-2])
                start = end - timedelta(days=months * 30)
            elif period.endswith('y'):
                years = int(period[:-1])
                start = end - timedelta(days=years * 365)
            else:
                raise ValueError(f"不支援的 period: {period}")
        
        # 查詢日 K 線
        kbars = self.api.kbars(
            contract=contract,
            start=start.strftime('%Y-%m-%d'),
            end=end.strftime('%Y-%m-%d'),
            timeout=5000  # 5 秒 timeout
        )
        
        if not kbars or not kbars.ts:
            return pd.DataFrame()
        
        # 轉換為 DataFrame（Kbars 物件有 ts, Open, High, Low, Close, Volume）
        df = pd.DataFrame({
            'Date': pd.to_datetime(kbars.ts),
            'Open': kbars.Open,
            'High': kbars.High,
            'Low': kbars.Low,
            'Close': kbars.Close,
            'Volume': kbars.Volume
        })
        
        df.set_index('Date', inplace=True)
        return df
    
    def batch_get_historical(
        self,
        codes: List[str],
        period: str = '60d'
    ) -> Dict[str, pd.DataFrame]:
        """
        批次查詢歷史資料
        
        Args:
            codes: 股票代碼列表
            period: 查詢期間
        
        Returns:
            {code: DataFrame}
        """
        results = {}
        
        for i, code in enumerate(codes):
            try:
                df = self.get_historical_data(code, period=period)
                results[code] = df
                
                # 進度顯示
                if (i + 1) % 100 == 0:
                    print(f"已查詢 {i + 1}/{len(codes)} 檔...")
                
                # 避免 API 限流
                if i < len(codes) - 1:
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"⚠️ {code} 查詢失敗: {e}")
                continue
        
        return results


def test_snapshot():
    """測試快照查詢"""
    print("測試批次快照查詢")
    print("=" * 60)
    
    with SinopacFetcher() as fetcher:
        # 測試 10 檔股票
        codes = ['2330', '2317', '2454', '2308', '6505', 
                 '3711', '2382', '2881', '2412', '2891']
        
        df = fetcher.get_snapshot(codes)
        print(f"\n查詢到 {len(df)} 檔股票:")
        print(df[['code', 'close', 'change_rate', 'volume']])


def test_historical():
    """測試歷史資料查詢"""
    print("\n測試歷史資料查詢")
    print("=" * 60)
    
    with SinopacFetcher() as fetcher:
        df = fetcher.get_historical_data('2330', period='30d')
        print(f"\n台積電最近 30 天資料（{len(df)} 筆）:")
        print(df.tail())


if __name__ == '__main__':
    test_snapshot()
    test_historical()
