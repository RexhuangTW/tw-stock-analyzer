"""選股策略整合測試"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from src.screener.strategies import (
    screen_rsi_oversold,
    screen_golden_cross,
    screen_momentum
)


@pytest.fixture
def mock_stock_data():
    """模擬股票資料"""
    dates = pd.date_range('2025-01-01', periods=30)
    close = pd.Series(100 + np.cumsum(np.random.randn(30)))
    
    return pd.DataFrame({
        'date': dates,
        'open': close - 1,
        'high': close + 2,
        'low': close - 2,
        'close': close,
        'volume': np.random.randint(1000, 5000, 30)
    })


class TestRSIOversoldStrategy:
    """RSI 超賣策略測試"""
    
    @patch('src.screener.strategies.TWSEFetcher')
    def test_rsi_oversold_found(self, mock_fetcher_class, mock_stock_data):
        """測試找到 RSI 超賣標的"""
        # 製造 RSI 超賣資料
        mock_instance = Mock()
        
        # 建立低 RSI 資料
        df = mock_stock_data.copy()
        df['close'] = pd.Series(range(100, 70, -1))  # 持續下跌 → RSI 低
        
        mock_instance.get_historical_price.return_value = df
        mock_fetcher_class.return_value = mock_instance
        
        result = screen_rsi_oversold(['2330'], rsi_threshold=40)
        
        # 應該找到超賣標的
        assert not result.empty
        assert 'rsi' in result.columns
    
    @patch('src.screener.strategies.TWSEFetcher')
    def test_rsi_oversold_not_found(self, mock_fetcher_class, mock_stock_data):
        """測試無超賣標的"""
        mock_instance = Mock()
        
        # 建立高 RSI 資料
        df = mock_stock_data.copy()
        df['close'] = pd.Series(range(70, 100))  # 持續上漲 → RSI 高
        
        mock_instance.get_historical_price.return_value = df
        mock_fetcher_class.return_value = mock_instance
        
        result = screen_rsi_oversold(['2330'], rsi_threshold=30)
        
        # 不應該找到
        assert result.empty


class TestGoldenCrossStrategy:
    """黃金交叉策略測試"""
    
    @patch('src.screener.strategies.TWSEFetcher')
    def test_golden_cross_detection(self, mock_fetcher_class):
        """測試黃金交叉偵測"""
        mock_instance = Mock()
        
        # 建立黃金交叉資料
        dates = pd.date_range('2025-01-01', periods=50)
        prices = [90] * 20 + list(range(90, 120))  # 先盤整後上漲
        
        df = pd.DataFrame({
            'date': dates,
            'close': prices,
            'open': prices,
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'volume': [1000] * 50
        })
        
        mock_instance.get_historical_price.return_value = df
        mock_fetcher_class.return_value = mock_instance
        
        result = screen_golden_cross(['2330'])
        
        # 檢查是否正確執行
        mock_instance.get_historical_price.assert_called_once()


class TestMomentumStrategy:
    """動能策略測試"""
    
    @patch('src.screener.strategies.TWSEFetcher')
    def test_momentum_detection(self, mock_fetcher_class):
        """測試動能偵測"""
        mock_instance = Mock()
        
        # 建立連續上漲資料
        dates = pd.date_range('2025-01-01', periods=30)
        prices = list(range(100, 130))
        
        df = pd.DataFrame({
            'date': dates,
            'close': prices,
            'open': prices,
            'high': prices,
            'low': prices,
            'volume': list(range(1000, 1300, 10))  # 量能放大
        })
        
        mock_instance.get_historical_price.return_value = df
        mock_fetcher_class.return_value = mock_instance
        
        result = screen_momentum(['2330'], min_volume=1000)
        
        # 應該找到動能標的
        assert not result.empty
    
    @patch('src.screener.strategies.TWSEFetcher')
    def test_momentum_insufficient_data(self, mock_fetcher_class):
        """測試資料不足情況"""
        mock_instance = Mock()
        
        # 只有 2 筆資料
        df = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=2),
            'close': [100, 101],
            'open': [99, 100],
            'high': [101, 102],
            'low': [99, 100],
            'volume': [1000, 1100]
        })
        
        mock_instance.get_historical_price.return_value = df
        mock_fetcher_class.return_value = mock_instance
        
        result = screen_momentum(['2330'])
        
        # 資料不足,不應找到
        assert result.empty
