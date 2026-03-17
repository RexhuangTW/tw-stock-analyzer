"""監控模組測試"""
import pytest
import pandas as pd
from src.monitor.watcher import StockWatcher, console_alert_handler, file_alert_handler


class TestStockWatcher:
    """股票監控器測試"""
    
    def test_initialization(self):
        """測試初始化"""
        watcher = StockWatcher(check_interval=60)
        assert watcher.check_interval == 60
        assert len(watcher.watchlist) == 0
        assert len(watcher.alert_handlers) == 0
    
    def test_add_stock(self):
        """測試加入股票"""
        watcher = StockWatcher()
        result = watcher.add_stock('2330', {'price_above': 1000})
        
        assert result is watcher  # 鏈式呼叫
        assert '2330' in watcher.watchlist
        assert watcher.watchlist['2330']['conditions']['price_above'] == 1000
    
    def test_remove_stock(self):
        """測試移除股票"""
        watcher = StockWatcher()
        watcher.add_stock('2330')
        watcher.remove_stock('2330')
        
        assert '2330' not in watcher.watchlist
    
    def test_add_alert_handler(self):
        """測試加入警報處理器"""
        watcher = StockWatcher()
        result = watcher.add_alert_handler(console_alert_handler)
        
        assert result is watcher
        assert len(watcher.alert_handlers) == 1
    
    def test_check_conditions_price_above(self):
        """測試價格突破條件"""
        watcher = StockWatcher()
        
        data = pd.Series({
            'close': 1100,
            'volume': 50000,
            'rsi': 60
        })
        
        conditions = {'price_above': 1000}
        alerts = watcher._check_conditions('2330', data, conditions)
        
        assert len(alerts) > 0
        assert '突破' in alerts[0]
    
    def test_check_conditions_no_trigger(self):
        """測試未觸發條件"""
        watcher = StockWatcher()
        
        data = pd.Series({
            'close': 900,
            'volume': 50000,
            'rsi': 60
        })
        
        conditions = {'price_above': 1000}
        alerts = watcher._check_conditions('2330', data, conditions)
        
        assert len(alerts) == 0


class TestAlertHandlers:
    """警報處理器測試"""
    
    def test_console_handler(self, capsys):
        """測試 console 處理器"""
        console_alert_handler('2330', '測試警報')
        captured = capsys.readouterr()
        assert '2330' in captured.out
        assert '測試警報' in captured.out
    
    def test_file_handler(self, tmp_path):
        """測試檔案處理器"""
        log_file = tmp_path / "test.log"
        handler = file_alert_handler(str(log_file))
        
        handler('2330', '測試警報')
        
        assert log_file.exists()
        content = log_file.read_text()
        assert '2330' in content
        assert '測試警報' in content
