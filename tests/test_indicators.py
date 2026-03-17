"""技術指標單元測試"""
import pytest
import pandas as pd
import numpy as np
from src.indicators.technical import (
    calculate_ma,
    calculate_rsi,
    calculate_macd,
    calculate_kd,
    calculate_bollinger_bands
)


@pytest.fixture
def sample_prices():
    """測試用價格資料"""
    return pd.Series([
        100, 102, 101, 103, 105, 104, 106, 108, 107, 109,
        111, 110, 112, 114, 113, 115, 117, 116, 118, 120
    ])


@pytest.fixture
def sample_ohlc():
    """測試用 OHLC 資料"""
    return pd.DataFrame({
        'open': [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
        'high': [103, 104, 104, 106, 107, 107, 109, 110, 110, 112],
        'low': [99, 101, 100, 102, 104, 103, 105, 107, 106, 108],
        'close': [102, 103, 102, 105, 106, 105, 108, 109, 108, 111]
    })


class TestMA:
    """移動平均線測試"""
    
    def test_ma_calculation(self, sample_prices):
        """測試 MA 計算"""
        ma5 = calculate_ma(sample_prices, 5)
        
        # 前 4 筆應該是 NaN
        assert pd.isna(ma5.iloc[:4]).all()
        
        # 第 5 筆開始有值
        assert not pd.isna(ma5.iloc[4])
        
        # 手動驗證第 5 筆 (100+102+101+103+105)/5 = 102.2
        assert abs(ma5.iloc[4] - 102.2) < 0.01
    
    def test_ma_length(self, sample_prices):
        """測試 MA 結果長度"""
        ma5 = calculate_ma(sample_prices, 5)
        assert len(ma5) == len(sample_prices)
    
    def test_ma_different_periods(self, sample_prices):
        """測試不同週期的 MA"""
        ma3 = calculate_ma(sample_prices, 3)
        ma10 = calculate_ma(sample_prices, 10)
        
        # MA3 第 3 筆開始有值
        assert not pd.isna(ma3.iloc[2])
        assert pd.isna(ma3.iloc[1])
        
        # MA10 第 10 筆開始有值
        assert not pd.isna(ma10.iloc[9])
        assert pd.isna(ma10.iloc[8])


class TestRSI:
    """RSI 測試"""
    
    def test_rsi_range(self, sample_prices):
        """測試 RSI 範圍 (0-100)"""
        rsi = calculate_rsi(sample_prices, period=14)
        
        # 移除 NaN
        rsi_valid = rsi.dropna()
        
        # RSI 應該在 0-100 之間
        assert (rsi_valid >= 0).all()
        assert (rsi_valid <= 100).all()
    
    def test_rsi_uptrend(self):
        """測試上升趨勢的 RSI (應該偏高)"""
        uptrend = pd.Series(range(100, 120))  # 持續上漲
        rsi = calculate_rsi(uptrend, period=14)
        
        # 最後的 RSI 應該 > 50
        assert rsi.iloc[-1] > 50
    
    def test_rsi_downtrend(self):
        """測試下降趨勢的 RSI (應該偏低)"""
        downtrend = pd.Series(range(120, 100, -1))  # 持續下跌
        rsi = calculate_rsi(downtrend, period=14)
        
        # 最後的 RSI 應該 < 50
        assert rsi.iloc[-1] < 50
    
    def test_rsi_length(self, sample_prices):
        """測試 RSI 結果長度"""
        rsi = calculate_rsi(sample_prices, period=14)
        assert len(rsi) == len(sample_prices)


class TestMACD:
    """MACD 測試"""
    
    def test_macd_columns(self, sample_prices):
        """測試 MACD 回傳欄位"""
        macd_df = calculate_macd(sample_prices)
        
        assert 'macd' in macd_df.columns
        assert 'signal' in macd_df.columns
        assert 'histogram' in macd_df.columns
    
    def test_macd_histogram(self, sample_prices):
        """測試 MACD 柱狀圖 = MACD - Signal"""
        macd_df = calculate_macd(sample_prices)
        
        # 計算誤差
        expected_histogram = macd_df['macd'] - macd_df['signal']
        diff = (macd_df['histogram'] - expected_histogram).abs()
        
        # 應該非常接近 (浮點誤差容許)
        assert (diff < 0.0001).all()
    
    def test_macd_length(self, sample_prices):
        """測試 MACD 結果長度"""
        macd_df = calculate_macd(sample_prices)
        assert len(macd_df) == len(sample_prices)
    
    def test_macd_custom_periods(self, sample_prices):
        """測試自訂 MACD 參數"""
        macd_df = calculate_macd(sample_prices, fast=5, slow=10, signal=5)
        
        assert not macd_df['macd'].isna().all()
        assert not macd_df['signal'].isna().all()


class TestKD:
    """KD 指標測試"""
    
    def test_kd_columns(self, sample_ohlc):
        """測試 KD 回傳欄位"""
        kd_df = calculate_kd(
            sample_ohlc['high'],
            sample_ohlc['low'],
            sample_ohlc['close']
        )
        
        assert 'k' in kd_df.columns
        assert 'd' in kd_df.columns
    
    def test_kd_range(self, sample_ohlc):
        """測試 KD 範圍 (0-100)"""
        kd_df = calculate_kd(
            sample_ohlc['high'],
            sample_ohlc['low'],
            sample_ohlc['close'],
            period=9
        )
        
        # 移除 NaN
        k_valid = kd_df['k'].dropna()
        d_valid = kd_df['d'].dropna()
        
        # K 和 D 應該在 0-100 之間
        assert (k_valid >= 0).all() and (k_valid <= 100).all()
        assert (d_valid >= 0).all() and (d_valid <= 100).all()
    
    def test_kd_length(self, sample_ohlc):
        """測試 KD 結果長度"""
        kd_df = calculate_kd(
            sample_ohlc['high'],
            sample_ohlc['low'],
            sample_ohlc['close']
        )
        
        assert len(kd_df) == len(sample_ohlc)


class TestBollingerBands:
    """布林通道測試"""
    
    def test_bb_columns(self, sample_prices):
        """測試布林通道回傳欄位"""
        bb_df = calculate_bollinger_bands(sample_prices)
        
        assert 'upper' in bb_df.columns
        assert 'middle' in bb_df.columns
        assert 'lower' in bb_df.columns
    
    def test_bb_order(self, sample_prices):
        """測試布林通道順序 (upper >= middle >= lower)"""
        bb_df = calculate_bollinger_bands(sample_prices)
        
        # 移除 NaN
        valid_idx = bb_df.dropna().index
        
        # upper >= middle
        assert (bb_df.loc[valid_idx, 'upper'] >= bb_df.loc[valid_idx, 'middle']).all()
        
        # middle >= lower
        assert (bb_df.loc[valid_idx, 'middle'] >= bb_df.loc[valid_idx, 'lower']).all()
    
    def test_bb_middle_is_ma(self, sample_prices):
        """測試布林通道中線 = MA"""
        bb_df = calculate_bollinger_bands(sample_prices, period=20)
        ma20 = calculate_ma(sample_prices, 20)
        
        # 移除 NaN 後比較
        valid_idx = bb_df.dropna().index
        diff = (bb_df.loc[valid_idx, 'middle'] - ma20.loc[valid_idx]).abs()
        
        assert (diff < 0.0001).all()
    
    def test_bb_custom_std(self, sample_prices):
        """測試自訂標準差倍數"""
        bb_1std = calculate_bollinger_bands(sample_prices, std_dev=1.0)
        bb_2std = calculate_bollinger_bands(sample_prices, std_dev=2.0)
        
        # 2 倍標準差的通道應該更寬
        valid_idx = bb_1std.dropna().index
        
        width_1std = bb_1std.loc[valid_idx, 'upper'] - bb_1std.loc[valid_idx, 'lower']
        width_2std = bb_2std.loc[valid_idx, 'upper'] - bb_2std.loc[valid_idx, 'lower']
        
        assert (width_2std > width_1std).all()
