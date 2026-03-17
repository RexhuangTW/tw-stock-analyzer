"""快速測試資料擷取"""
import sys
from src.data.fetcher import TWSEFetcher

def test_daily_price():
    """測試抓取台積電 (2330) 日成交資料"""
    fetcher = TWSEFetcher()
    
    print("📊 測試抓取台積電 (2330) 本月成交資料...")
    try:
        df = fetcher.get_daily_price("2330")
        print(f"✅ 成功! 取得 {len(df)} 筆資料")
        print("\n前 5 筆:")
        print(df.head())
        print("\n欄位:", df.columns.tolist())
    except Exception as e:
        print(f"❌ 失敗: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_daily_price()
    sys.exit(0 if success else 1)
