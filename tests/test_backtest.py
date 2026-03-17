"""回測引擎單元測試"""
import pytest
import pandas as pd
import numpy as np
from src.backtest.engine import BacktestEngine, sma_crossover_strategy, rsi_strategy


@pytest.fixture
def sample_data():
    """測試用歷史資料"""
    dates = pd.date_range(start='2025-01-01', periods=100, freq='D')
    np.random.seed(42)
    base_price = 100
    prices = [base_price]
    
    for _ in range(99):
        change = np.random.randn() * 2
        prices.append(prices[-1] + change)
    
    return pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 10000, 100)
    })


class TestBacktestEngine:
    """回測引擎基礎測試"""
    
    def test_initialization(self):
        """測試初始化"""
        engine = BacktestEngine(initial_capital=1000000)
        assert engine.cash == 1000000
        assert engine.position == 0
    
    def test_buy_success(self):
        """測試買入成功"""
        engine = BacktestEngine(initial_capital=1000000)
        success = engine.buy(pd.Timestamp('2025-01-01'), 100, 5)
        assert success is True
        assert engine.position == 5
    
    def test_sell_success(self):
        """測試賣出成功"""
        engine = BacktestEngine(initial_capital=1000000)
        engine.buy(pd.Timestamp('2025-01-01'), 100, 5)
        success = engine.sell(pd.Timestamp('2025-01-02'), 105, 5)
        assert success is True
        assert engine.position == 0
    
    def test_run_returns_statistics(self, sample_data):
        """測試回測回傳統計資料"""
        engine = BacktestEngine(initial_capital=1000000)
        strategy = sma_crossover_strategy(5, 20)
        result = engine.run(sample_data, strategy)
        
        assert 'total_return' in result
        assert 'max_drawdown' in result
        assert 'total_trades' in result
