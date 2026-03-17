"""資料擷取模組測試"""
import pytest
import pandas as pd
from src.data.cache import DataCache, cached


class TestDataCache:
    """快取機制測試"""
    
    def test_set_and_get(self):
        """測試讀寫"""
        cache = DataCache(cache_dir="test_cache", ttl_hours=1)
        cache.set("test", {"data": 123})
        result = cache.get("test")
        assert result == {"data": 123}
        cache.clear()
    
    def test_get_nonexistent(self):
        """測試不存在的鍵"""
        cache = DataCache(cache_dir="test_cache")
        result = cache.get("nonexistent")
        assert result is None
        cache.clear()
    
    def test_cached_decorator(self):
        """測試裝飾器"""
        call_count = [0]
        
        @cached(ttl_hours=1)
        def test_func(x):
            call_count[0] += 1
            return x * 2
        
        result1 = test_func(10)
        result2 = test_func(10)
        
        assert result1 == result2 == 20
        assert call_count[0] == 1  # 只呼叫一次
        
        # 清理
        from src.data.cache import _cache
        _cache.clear()


class TestYahooFetcher:
    """Yahoo Finance 測試"""
    
    def test_tw_symbol_conversion(self):
        """測試台股代號轉換"""
        from src.data.yahoo_fetcher import YahooFetcher
        
        assert YahooFetcher.tw_symbol("2330", "TWSE") == "2330.TW"
        assert YahooFetcher.tw_symbol("6488", "TPEX") == "6488.TWO"
