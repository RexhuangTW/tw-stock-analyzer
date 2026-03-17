"""進階技術指標測試"""
import pytest
import pandas as pd
import numpy as np
from src.indicators.advanced import (
    calculate_atr,
    calculate_obv,
    calculate_cci,
    calculate_williams_r,
    calculate_vwap
)


@pytest.fixture
def sample_ohlcv():
    """測試用 OHLCV 資料"""
    np.random.seed(42)
    n = 50
    close = pd.Series(100 + np.cumsum(np.random.randn(n)))
    return pd.DataFrame({
        'high': close + np.random.rand(n) * 2,
        'low': close - np.random.rand(n) * 2,
        'close': close,
        'volume': pd.Series(np.random.randint(1000, 5000, n))
    })


class TestAdvancedIndicators:
    """進階指標測試"""
    
    def test_atr_calculation(self, sample_ohlcv):
        """測試 ATR 計算"""
        atr = calculate_atr(
            sample_ohlcv['high'],
            sample_ohlcv['low'],
            sample_ohlcv['close']
        )
        assert len(atr) == len(sample_ohlcv)
        assert atr.dropna().min() >= 0
    
    def test_obv_calculation(self, sample_ohlcv):
        """測試 OBV 計算"""
        obv = calculate_obv(
            sample_ohlcv['close'],
            sample_ohlcv['volume']
        )
        assert len(obv) == len(sample_ohlcv)
    
    def test_cci_calculation(self, sample_ohlcv):
        """測試 CCI 計算"""
        cci = calculate_cci(
            sample_ohlcv['high'],
            sample_ohlcv['low'],
            sample_ohlcv['close']
        )
        assert len(cci) == len(sample_ohlcv)
    
    def test_williams_r_range(self, sample_ohlcv):
        """測試威廉指標範圍"""
        williams = calculate_williams_r(
            sample_ohlcv['high'],
            sample_ohlcv['low'],
            sample_ohlcv['close']
        )
        valid = williams.dropna()
        assert (valid >= -100).all()
        assert (valid <= 0).all()
    
    def test_vwap_calculation(self, sample_ohlcv):
        """測試 VWAP 計算"""
        vwap = calculate_vwap(
            sample_ohlcv['high'],
            sample_ohlcv['low'],
            sample_ohlcv['close'],
            sample_ohlcv['volume']
        )
        assert len(vwap) == len(sample_ohlcv)
        assert vwap.dropna().min() > 0
