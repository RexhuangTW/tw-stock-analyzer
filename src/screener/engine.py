"""選股引擎"""
from typing import List, Callable
import pandas as pd


class ScreenerEngine:
    """選股篩選引擎"""
    
    def __init__(self):
        self.filters: List[Callable] = []
    
    def add_filter(self, filter_func: Callable) -> 'ScreenerEngine':
        """
        新增篩選條件
        
        Args:
            filter_func: 接受 DataFrame，回傳 boolean mask 的函數
        
        Returns:
            self (支援鏈式呼叫)
        """
        self.filters.append(filter_func)
        return self
    
    def run(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        執行篩選
        
        Args:
            stock_data: 股票資料 DataFrame
        
        Returns:
            篩選後的 DataFrame
        """
        result = stock_data.copy()
        
        for filter_func in self.filters:
            mask = filter_func(result)
            result = result[mask]
        
        return result
    
    def reset(self) -> 'ScreenerEngine':
        """清空所有篩選條件"""
        self.filters = []
        return self


# 常用篩選條件範例

def filter_price_above(min_price: float) -> Callable:
    """股價高於指定價格"""
    def _filter(df: pd.DataFrame) -> pd.Series:
        return df['close'] >= min_price
    return _filter


def filter_volume_above(min_volume: int) -> Callable:
    """成交量大於指定值"""
    def _filter(df: pd.DataFrame) -> pd.Series:
        return df['volume'] >= min_volume
    return _filter


def filter_rsi_oversold(threshold: float = 30) -> Callable:
    """RSI 超賣 (< threshold)"""
    def _filter(df: pd.DataFrame) -> pd.Series:
        return df['rsi'] < threshold
    return _filter


def filter_rsi_overbought(threshold: float = 70) -> Callable:
    """RSI 超買 (> threshold)"""
    def _filter(df: pd.DataFrame) -> pd.Series:
        return df['rsi'] > threshold
    return _filter


def filter_golden_cross() -> Callable:
    """黃金交叉 (短均線上穿長均線)"""
    def _filter(df: pd.DataFrame) -> pd.Series:
        # 需要有 ma_short, ma_long, ma_short_prev, ma_long_prev
        return (df['ma_short'] > df['ma_long']) & \
               (df['ma_short_prev'] <= df['ma_long_prev'])
    return _filter
