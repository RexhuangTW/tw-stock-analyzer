"""修正 import 路徑 - 在任何環境下都能運作"""
import sys
import os

# 取得專案根目錄的絕對路徑
project_root = os.path.dirname(os.path.abspath(__file__))

# 確保專案根目錄在 Python 路徑的最前面
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 驗證
if __name__ == "__main__":
    print(f"專案根目錄: {project_root}")
    print(f"\nPython 路徑 (前 3 項):")
    for i, p in enumerate(sys.path[:3], 1):
        print(f"  {i}. {p}")
    
    print("\n測試 import...")
    try:
        from src.data.fetcher import TWSEFetcher
        print("✅ src.data.fetcher 可用")
    except ImportError as e:
        print(f"❌ 失敗: {e}")
