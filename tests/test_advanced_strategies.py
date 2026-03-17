"""進階選股策略測試"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from src.screener.advanced_strategies import (
    screen_breakout_with_volume,
    screen_bollinger_squeeze,
    screen_multi_factor
)


@pytest.fixture
def breakout_data():
    """突破測試資料"""
    dates = pd.date_range('2025-01-01', periods=40)
    
    # 前 30 天在 100 附近整理,最後突破
    prices = [100 + np.random.randn() for _ in range(30)] + list(range(105, 115))
    volumes = [1000 + np.random.randint(-200, 200) for _ in range(30)] + list(range(2000, 2200, 20))
    
    return pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p + 2 for p in prices],
        'low': [p - 2 for p in prices],
        'close': prices,
        'volume': volumes
    })


@pytest.fixture
def squeeze_data():
    """布林收縮測試資料"""
    dates = pd.date_range('2025-01-01', periods=30)
    
    # 價格收縮
    prices = [100 + np.random.randn() * 0.5 for _ in range(30)]
    
    return pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p + 0.5 for p in prices],
        'low': [p - 0.5 for p in prices],
        'close': prices,
        'volume': [1000] * 30
    })


class TestBreakoutStrategy:
    """量價突破策略測試"""
    
    @patch('src.screener.advanced_strategies.TWSEFetcher')
    def test_breakout_detection(self, mock_fetcher_class, breakout_data):
        """測試突破偵測"""
        mock_instance = Mock()
        mock_instance.get_historical_price.return_value = breakout_data
        mock_fetcher_class.return_value = mock_instance
        
        result = screen_breakout_with_volume(['2330'], lookback_days=20)
        
        # 測試執行無異常
        mock_instance.get_historical_price.assert_called()
    
    @patch('src.screener.advanced_strategies.TWSEFetcher')
    def test_no_breakout(self, mock_fetcher_class):
        """測試無突破"""
        mock_instance = Mock()
        
        # 平穩資料
        dates = pd.date_range('2025-01-01', periods=30)
        df = pd.DataFrame({
            'date': dates,
            'close': [100] * 30,
            'high': [102] * 30,
            'low': [98] * 30,
            'open': [100] * 30,
            'volume': [1000] * 30
        })
        
        mock_instance.get_historical_price.return_value = df
        mock_fetcher_class.return_value = mock_instance
        
        result = screen_breakout_with_volume(['2330'])
        
        # 不應該找到
        assert result.empty


class TestBollingerSqueezeStrategy:
    """布林收縮策略測試"""
    
    @patch('src.screener.advanced_strategies.TWSEFetcher')
    def test_squeeze_detection(self, mock_fetcher_class, squeeze_data):
        """測試收縮偵測"""
        mock_instance = Mock()
        mock_instance.get_historical_price.return_value = squeeze_data
        mock_fetcher_class.return_value = mock_instance
        
        result = screen_bollinger_squeeze(['2330'], squeeze_threshold=0.05)
        
        # 應該偵測到收縮
        assert not result.empty
        assert 'bandwidth' in result.columns


class TestMultiFactorStrategy:
    """多因子策略測試"""
    
    @patch('src.screener.advanced_strategies.TWSEFetcher')
    def test_multi_factor_scoring(self, mock_fetcher_class):
        """測試綜合評分"""
        mock_instance = Mock()
        
        # 建立測試資料
        dates = pd.date_range('2025-01-01', periods=100)
        prices = list(range(80, 180))
        
        df = pd.DataFrame({
            'date': dates,
            'close': prices,
            'high': [p + 2 for p in prices],
            'low': [p - 2 for p in prices],
            'open': prices,
            'volume': list(range(1000, 1100))
        })
        
        mock_instance.get_historical_price.return_value = df
        mock_fetcher_class.return_value = mock_instance
        
        result = screen_multi_factor(['2330'])
        
        # 應該有評分
        assert not result.empty
        assert 'total_score' in result.columns
        assert result.iloc[0]['total_score'] >= 0
        assert result.iloc[0]['total_score'] <= 100
    
    @patch('src.screener.advanced_strategies.TWSEFetcher')
    def test_custom_weights(self, mock_fetcher_class):
        """測試自訂權重"""
        mock_instance = Mock()
        
        dates = pd.date_range('2025-01-01', periods=80)
        df = pd.DataFrame({
            'date': dates,
            'close': range(100, 180),
            'high': range(102, 182),
            'low': range(98, 178),
            'open': range(100, 180),
            'volume': [1000] * 80
        })
        
        mock_instance.get_historical_price.return_value = df
        mock_fetcher_class.return_value = mock_instance
        
        weights = {
            'trend': 0.5,
            'momentum': 0.3,
            'volatility': 0.1,
            'volume': 0.1
        }
        
        result = screen_multi_factor(['2330'], weights=weights)
        
        assert not result.empty
