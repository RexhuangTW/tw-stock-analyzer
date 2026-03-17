"""測試技術指標計算"""
from src.data.fetcher import TWSEFetcher
from src.indicators.technical import calculate_ma, calculate_rsi, calculate_macd

def test_indicators():
    """測試指標計算"""
    fetcher = TWSEFetcher()
    df = fetcher.get_daily_price("2330")
    
    print("📊 台積電 3 月成交資料:")
    print(df[['date', 'close', 'volume']].tail(5))
    
    # MA
    df['ma5'] = calculate_ma(df['close'], 5)
    df['ma20'] = calculate_ma(df['close'], 20)
    print("\n📈 移動平均線 (MA5, MA20):")
    print(df[['date', 'close', 'ma5', 'ma20']].tail(5))
    
    # RSI
    df['rsi'] = calculate_rsi(df['close'], period=14)
    print("\n💪 RSI (14):")
    print(df[['date', 'close', 'rsi']].tail(5))
    
    # MACD
    macd_df = calculate_macd(df['close'])
    df = df.join(macd_df)
    print("\n📉 MACD:")
    print(df[['date', 'close', 'macd', 'signal', 'histogram']].tail(5))
    
    print("\n✅ 所有指標計算成功!")

if __name__ == "__main__":
    test_indicators()
