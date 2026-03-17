"""視覺化模組測試"""
import pytest
import pandas as pd
import numpy as np
from src.visualization.plotly_charts import (
    create_candlestick_chart,
    create_technical_chart,
    create_backtest_chart
)


@pytest.fixture
def sample_chart_data():
    """測試用圖表資料"""
    np.random.seed(42)
    dates = pd.date_range('2025-01-01', periods=30)
    close = pd.Series(100 + np.cumsum(np.random.randn(30)))
    
    return pd.DataFrame({
        'date': dates,
        'open': close - np.random.rand(30),
        'high': close + np.random.rand(30) * 2,
        'low': close - np.random.rand(30) * 2,
        'close': close,
        'volume': np.random.randint(1000, 5000, 30)
    })


class TestPlotlyCharts:
    """Plotly 圖表測試"""
    
    def test_candlestick_creation(self, sample_chart_data):
        """測試 K 線圖生成"""
        fig = create_candlestick_chart(
            sample_chart_data,
            title="Test Chart",
            show_volume=True
        )
        assert fig is not None
        assert hasattr(fig, 'data')
        assert len(fig.data) >= 1
    
    def test_technical_chart_creation(self, sample_chart_data):
        """測試技術指標圖生成"""
        rsi = pd.Series(np.random.rand(30) * 100)
        macd_df = pd.DataFrame({
            'macd': np.random.randn(30),
            'signal': np.random.randn(30),
            'histogram': np.random.randn(30)
        })
        
        fig = create_technical_chart(
            sample_chart_data,
            rsi=rsi,
            macd=macd_df
        )
        assert fig is not None
        assert hasattr(fig, 'data')
    
    def test_backtest_chart_creation(self):
        """測試回測圖生成"""
        equity_curve = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=30),
            'total_equity': 1000000 + np.cumsum(np.random.randn(30) * 10000),
            'peak': 1000000 + np.cumsum(np.random.rand(30) * 5000),
            'returns': np.random.randn(30) * 0.01,
            'drawdown': -np.random.rand(30) * 0.05
        })
        
        fig = create_backtest_chart(
            equity_curve,
            trades=None,
            title="Test Backtest"
        )
        assert fig is not None
        assert hasattr(fig, 'data')
