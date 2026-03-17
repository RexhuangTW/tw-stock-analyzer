"""matplotlib 圖表測試"""
import pytest
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 無 GUI 後端
import matplotlib.pyplot as plt
from src.visualization.charts import (
    plot_candlestick,
    plot_technical_indicators,
    plot_backtest_results
)


@pytest.fixture
def sample_ohlcv():
    """測試用 OHLCV 資料"""
    np.random.seed(42)
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


@pytest.fixture
def sample_indicator_data(sample_ohlcv):
    """測試用指標資料"""
    df = sample_ohlcv.copy()
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    df['rsi'] = pd.Series(np.random.rand(30) * 100)
    df['macd'] = pd.Series(np.random.randn(30))
    df['signal'] = pd.Series(np.random.randn(30))
    df['histogram'] = df['macd'] - df['signal']
    return df


@pytest.fixture
def sample_backtest_data():
    """測試用回測資料"""
    dates = pd.date_range('2025-01-01', periods=30)
    
    equity_curve = pd.DataFrame({
        'date': dates,
        'total_equity': 1000000 + np.cumsum(np.random.randn(30) * 10000),
        'peak': 1000000 + np.cumsum(np.random.rand(30) * 5000),
        'returns': np.random.randn(30) * 0.01,
        'drawdown': -np.random.rand(30) * 0.05
    })
    
    trades = pd.DataFrame({
        'date': dates[:5],
        'action': ['BUY', 'SELL', 'BUY', 'SELL', 'BUY'],
        'price': [100, 105, 103, 108, 106],
        'shares': [10, 10, 15, 15, 20]
    })
    
    return equity_curve, trades


class TestCandlestickChart:
    """K線圖測試"""
    
    def test_plot_creation(self, sample_ohlcv):
        """測試圖表生成"""
        fig = plot_candlestick(sample_ohlcv, title="Test", save_path=None)
        
        assert fig is not None
        assert isinstance(fig, matplotlib.figure.Figure)
        
        plt.close(fig)
    
    def test_plot_with_volume(self, sample_ohlcv):
        """測試包含成交量"""
        fig = plot_candlestick(sample_ohlcv, show_volume=True, save_path=None)
        
        # 應該有 2 個子圖 (價格 + 成交量)
        assert len(fig.axes) == 2
        
        plt.close(fig)
    
    def test_plot_without_volume(self, sample_ohlcv):
        """測試不含成交量"""
        fig = plot_candlestick(sample_ohlcv, show_volume=False, save_path=None)
        
        # 應該只有 1 個子圖
        assert len(fig.axes) == 1
        
        plt.close(fig)


class TestTechnicalIndicatorChart:
    """技術指標圖測試"""
    
    def test_plot_creation(self, sample_indicator_data):
        """測試圖表生成"""
        fig = plot_technical_indicators(
            sample_indicator_data,
            indicators=['ma5', 'ma20', 'rsi'],
            save_path=None
        )
        
        assert fig is not None
        assert isinstance(fig, matplotlib.figure.Figure)
        
        plt.close(fig)
    
    def test_plot_with_rsi(self, sample_indicator_data):
        """測試 RSI 子圖"""
        fig = plot_technical_indicators(
            sample_indicator_data,
            indicators=['rsi'],
            save_path=None
        )
        
        # 應該有多個子圖
        assert len(fig.axes) >= 2
        
        plt.close(fig)


class TestBacktestResultChart:
    """回測結果圖測試"""
    
    def test_plot_creation(self, sample_backtest_data):
        """測試圖表生成"""
        equity_curve, trades = sample_backtest_data
        
        fig = plot_backtest_results(
            equity_curve,
            trades,
            save_path=None
        )
        
        assert fig is not None
        assert isinstance(fig, matplotlib.figure.Figure)
        
        plt.close(fig)
    
    def test_plot_without_trades(self, sample_backtest_data):
        """測試無交易紀錄"""
        equity_curve, _ = sample_backtest_data
        
        fig = plot_backtest_results(
            equity_curve,
            pd.DataFrame(),  # 空交易紀錄
            save_path=None
        )
        
        assert fig is not None
        
        plt.close(fig)
    
    def test_plot_structure(self, sample_backtest_data):
        """測試圖表結構"""
        equity_curve, trades = sample_backtest_data
        
        fig = plot_backtest_results(equity_curve, trades, save_path=None)
        
        # 應該有 3 個子圖 (淨值/報酬/回撤)
        assert len(fig.axes) == 3
        
        plt.close(fig)
