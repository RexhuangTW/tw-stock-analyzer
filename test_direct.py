#!/usr/bin/env python3
"""測試直接執行時的 import"""

import sys
import os

# 和 app.py 一樣的路徑設定
_project_root = os.path.dirname(os.path.abspath(__file__))
print(f"專案根目錄: {_project_root}")
print(f"目錄存在: {os.path.exists(_project_root)}")
print(f"src 存在: {os.path.exists(os.path.join(_project_root, 'src'))}")

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

print(f"\nsys.path 前 3 項:")
for i, p in enumerate(sys.path[:3], 1):
    print(f"  {i}. {p}")

print("\n測試 import...")
try:
    from src.data.fetcher import TWSEFetcher
    print("✅ 成功！")
except Exception as e:
    print(f"❌ 失敗: {e}")
    import traceback
    traceback.print_exc()
