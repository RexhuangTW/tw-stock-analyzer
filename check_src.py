#!/usr/bin/env python3
"""檢查 src 目錄結構"""

import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, 'src')

print(f"src 目錄: {src_dir}")
print(f"存在: {os.path.exists(src_dir)}")
print(f"\nsrc 目錄內容:")

for item in sorted(os.listdir(src_dir)):
    item_path = os.path.join(src_dir, item)
    is_dir = os.path.isdir(item_path)
    marker = "📁" if is_dir else "📄"
    print(f"  {marker} {item}")
    
    if is_dir:
        # 檢查子目錄
        sub_items = os.listdir(item_path)
        has_init = "__init__.py" in sub_items
        init_marker = "✅" if has_init else "❌"
        print(f"     {init_marker} __init__.py")
        for sub in sorted(sub_items)[:3]:
            print(f"        - {sub}")

print("\n檢查 Python 是否能識別為套件:")
print(f"sys.path[0] = {project_root}")
sys.path.insert(0, project_root)

# 嘗試不同的 import 方式
print("\n測試 1: import src")
try:
    import src
    print(f"  ✅ 成功: {src}")
    print(f"     __file__: {getattr(src, '__file__', 'N/A')}")
    print(f"     __path__: {getattr(src, '__path__', 'N/A')}")
except Exception as e:
    print(f"  ❌ 失敗: {e}")

print("\n測試 2: import src.data")
try:
    import src.data
    print(f"  ✅ 成功")
except Exception as e:
    print(f"  ❌ 失敗: {e}")

print("\n測試 3: from src.data import fetcher")
try:
    from src.data import fetcher
    print(f"  ✅ 成功")
except Exception as e:
    print(f"  ❌ 失敗: {e}")
