"""資料快取模組"""
import os
import pickle
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any
import pandas as pd


class DataCache:
    """資料快取管理器"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Args:
            cache_dir: 快取目錄
            ttl_hours: 快取有效期限 (小時)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成快取鍵值"""
        key_str = f"{args}_{kwargs}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """取得快取檔案路徑"""
        return self.cache_dir / f"{key}.pkl"
    
    def get(self, key: str) -> Optional[Any]:
        """
        取得快取資料
        
        Args:
            key: 快取鍵值
        
        Returns:
            快取的資料,若不存在或過期則回傳 None
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        # 檢查是否過期
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - mtime > self.ttl:
            cache_path.unlink()  # 刪除過期快取
            return None
        
        # 讀取快取
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    
    def set(self, key: str, data: Any) -> None:
        """
        設定快取資料
        
        Args:
            key: 快取鍵值
            data: 要快取的資料
        """
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"⚠️ 快取寫入失敗: {e}")
    
    def clear(self) -> None:
        """清空所有快取"""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
    
    def clear_expired(self) -> int:
        """
        清除過期快取
        
        Returns:
            清除的檔案數量
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.pkl"):
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime > self.ttl:
                cache_file.unlink()
                count += 1
        return count


# 全域快取實例
_cache = DataCache()


def cached(ttl_hours: int = 24):
    """
    快取裝飾器
    
    Args:
        ttl_hours: 快取有效期限 (小時)
    
    Example:
        @cached(ttl_hours=12)
        def fetch_expensive_data(stock_id, date):
            # ... 耗時操作
            return data
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成快取鍵
            key = _cache._generate_key(func.__name__, *args, **kwargs)
            
            # 嘗試從快取取得
            cached_data = _cache.get(key)
            if cached_data is not None:
                return cached_data
            
            # 執行函數
            result = func(*args, **kwargs)
            
            # 儲存到快取
            _cache.set(key, result)
            
            return result
        
        return wrapper
    return decorator
