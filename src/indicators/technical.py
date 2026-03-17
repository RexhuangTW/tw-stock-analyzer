"""技術指標計算"""
import pandas as pd
import numpy as np


def calculate_ma(prices: pd.Series, period: int) -> pd.Series:
    """
    計算移動平均線 (Moving Average)
    
    Args:
        prices: 價格序列
        period: 週期 (e.g., 5, 20, 60)
    
    Returns:
        MA 序列
    """
    return prices.rolling(window=period).mean()


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    計算相對強弱指標 (RSI)
    
    Args:
        prices: 收盤價序列
        period: 週期，預設 14
    
    Returns:
        RSI 序列 (0-100)
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(prices: pd.Series, 
                   fast: int = 12, 
                   slow: int = 26, 
                   signal: int = 9) -> pd.DataFrame:
    """
    計算 MACD 指標
    
    Args:
        prices: 收盤價序列
        fast: 快線週期
        slow: 慢線週期
        signal: 訊號線週期
    
    Returns:
        DataFrame with columns: macd, signal, histogram
    """
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    
    return pd.DataFrame({
        'macd': macd,
        'signal': signal_line,
        'histogram': histogram
    })


def calculate_kd(high: pd.Series, 
                 low: pd.Series, 
                 close: pd.Series, 
                 period: int = 9) -> pd.DataFrame:
    """
    計算 KD 指標 (隨機指標)
    
    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        period: 週期
    
    Returns:
        DataFrame with columns: k, d
    """
    lowest_low = low.rolling(window=period).min()
    highest_high = high.rolling(window=period).max()
    
    rsv = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    
    k = rsv.ewm(com=2, adjust=False).mean()
    d = k.ewm(com=2, adjust=False).mean()
    
    return pd.DataFrame({'k': k, 'd': d})


def calculate_bollinger_bands(prices: pd.Series, 
                               period: int = 20, 
                               std_dev: float = 2.0) -> pd.DataFrame:
    """
    計算布林通道 (Bollinger Bands)
    
    Args:
        prices: 收盤價序列
        period: MA 週期
        std_dev: 標準差倍數
    
    Returns:
        DataFrame with columns: upper, middle, lower
    """
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    
    return pd.DataFrame({
        'upper': upper,
        'middle': middle,
        'lower': lower
    })
