import sys
import os
print("Python 路徑:")
for p in sys.path[:5]:
    print(f"  {p}")

print(f"\n當前目錄: {os.getcwd()}")
print(f"src 存在: {os.path.exists('src')}")
print(f"src/data 存在: {os.path.exists('src/data')}")

try:
    from src.data.fetcher import TWSEFetcher
    print("✅ 導入成功")
except Exception as e:
    print(f"❌ 導入失敗: {e}")
