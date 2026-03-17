"""選股引擎單元測試"""
import pytest
import pandas as pd
from src.screener.engine import (
    ScreenerEngine,
    filter_price_above,
    filter_volume_above,
    filter_rsi_oversold
)


@pytest.fixture
def sample_stock_data():
    """測試用股票資料"""
    return pd.DataFrame({
        'stock_id': ['2330', '2317', '2454', '2412', '2308'],
        'close': [950, 120, 1500, 90, 1200],
        'volume': [50000, 30000, 20000, 10000, 40000],
        'rsi': [45, 25, 75, 55, 30]
    })


class TestScreenerEngine:
    """選股引擎測試"""
    
    def test_add_filter(self):
        """測試新增篩選條件"""
        engine = ScreenerEngine()
        engine.add_filter(filter_price_above(100))
        assert len(engine.filters) == 1
    
    def test_run_single_filter(self, sample_stock_data):
        """測試單一篩選條件"""
        engine = ScreenerEngine()
        engine.add_filter(filter_price_above(1000))
        result = engine.run(sample_stock_data)
        assert len(result) == 2
    
    def test_run_multiple_filters(self, sample_stock_data):
        """測試多重篩選條件"""
        engine = ScreenerEngine()
        engine.add_filter(filter_price_above(100))
        engine.add_filter(filter_volume_above(25000))
        result = engine.run(sample_stock_data)
        assert len(result) == 3
