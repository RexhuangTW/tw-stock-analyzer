"""進階技術指標"""
import pandas as pd
import numpy as np


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    計算 ATR (Average True Range,真實波動幅度)
    
    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        period: 週期
    
    Returns:
        ATR 序列
    """
    # True Range = max(high-low, abs(high-close_prev), abs(low-close_prev))
    prev_close = close.shift(1)
    
    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR = EMA of TR
    atr = tr.ewm(span=period, adjust=False).mean()
    
    return atr


def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    計算 OBV (On-Balance Volume,能量潮)
    
    Args:
        close: 收盤價序列
        volume: 成交量序列
    
    Returns:
        OBV 序列
    """
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    return obv


def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    """
    計算 CCI (Commodity Channel Index)
    
    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        period: 週期
    
    Returns:
        CCI 序列
    """
    tp = (high + low + close) / 3  # Typical Price
    sma_tp = tp.rolling(window=period).mean()
    mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())  # Mean Absolute Deviation
    
    cci = (tp - sma_tp) / (0.015 * mad)
    
    return cci


def calculate_williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    計算威廉指標 (%R)
    
    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        period: 週期
    
    Returns:
        威廉指標序列 (-100 ~ 0)
    """
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()
    
    williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
    
    return williams_r


def calculate_vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    計算 VWAP (Volume Weighted Average Price,成交量加權平均價)
    
    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        volume: 成交量序列
    
    Returns:
        VWAP 序列
    """
    tp = (high + low + close) / 3  # Typical Price
    vwap = (tp * volume).cumsum() / volume.cumsum()
    
    return vwap


def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.DataFrame:
    """
    計算 ADX (Average Directional Index,平均趨向指數)
    
    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        period: 週期
    
    Returns:
        DataFrame with columns: adx, +di, -di
    """
    # True Range
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Directional Movement
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    
    # Smoothed values
    atr = tr.ewm(span=period, adjust=False).mean()
    plus_di = 100 * pd.Series(plus_dm).ewm(span=period, adjust=False).mean() / atr
    minus_di = 100 * pd.Series(minus_dm).ewm(span=period, adjust=False).mean() / atr
    
    # ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.ewm(span=period, adjust=False).mean()
    
    return pd.DataFrame({
        'adx': adx,
        '+di': plus_di,
        '-di': minus_di
    })


def calculate_ichimoku(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.DataFrame:
    """
    計算一目均衡表 (Ichimoku Cloud)
    
    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
    
    Returns:
        DataFrame with columns: tenkan, kijun, senkou_a, senkou_b, chikou
    """
    # 轉換線 (Tenkan-sen): (9日最高+9日最低)/2
    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
    
    # 基準線 (Kijun-sen): (26日最高+26日最低)/2
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
    
    # 先行帶A (Senkou Span A): (轉換線+基準線)/2,向前移26日
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    
    # 先行帶B (Senkou Span B): (52日最高+52日最低)/2,向前移26日
    senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
    
    # 遲行線 (Chikou Span): 當日收盤價,向後移26日
    chikou = close.shift(-26)
    
    return pd.DataFrame({
        'tenkan': tenkan,
        'kijun': kijun,
        'senkou_a': senkou_a,
        'senkou_b': senkou_b,
        'chikou': chikou
    })


def calculate_fibonacci_levels(high: pd.Series, low: pd.Series, lookback: int = 50) -> dict:
    """
    計算費波那契回調水準
    
    Args:
        high: 最高價序列
        low: 最低價序列
        lookback: 回顧週期
    
    Returns:
        dict with fibonacci levels
    """
    recent_high = high.tail(lookback).max()
    recent_low = low.tail(lookback).min()
    
    diff = recent_high - recent_low
    
    return {
        'level_0': recent_high,
        'level_236': recent_high - 0.236 * diff,
        'level_382': recent_high - 0.382 * diff,
        'level_500': recent_high - 0.500 * diff,
        'level_618': recent_high - 0.618 * diff,
        'level_786': recent_high - 0.786 * diff,
        'level_100': recent_low
    }
