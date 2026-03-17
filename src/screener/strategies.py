"""預設選股策略"""
from typing import List
import pandas as pd
from src.data.fetcher import TWSEFetcher
from src.indicators.technical import calculate_ma, calculate_rsi, calculate_macd
from src.screener.engine import ScreenerEngine, filter_price_above, filter_volume_above


def screen_rsi_oversold(stock_ids: List[str], rsi_threshold: float = 30) -> pd.DataFrame:
    """
    RSI 超賣策略：找出 RSI < 30 且成交量足夠的股票
    
    Args:
        stock_ids: 要篩選的股票代號清單
        rsi_threshold: RSI 門檻值
    
    Returns:
        符合條件的股票 DataFrame
    """
    fetcher = TWSEFetcher()
    results = []
    
    for stock_id in stock_ids:
        try:
            print(f"🔍 分析 {stock_id}...", end=" ")
            df = fetcher.get_historical_price(stock_id, months=2)
            
            # 計算指標
            df['rsi'] = calculate_rsi(df['close'], period=14)
            df['ma5'] = calculate_ma(df['close'], 5)
            
            # 取最新一筆
            latest = df.iloc[-1]
            
            if pd.notna(latest['rsi']) and latest['rsi'] < rsi_threshold:
                results.append({
                    'stock_id': stock_id,
                    'date': latest['date'],
                    'close': latest['close'],
                    'volume': latest['volume'],
                    'rsi': latest['rsi'],
                    'ma5': latest['ma5']
                })
                rsi_val = latest['rsi']
                print(f"✅ RSI={rsi_val:.1f}")
            else:
                rsi_val = latest['rsi']
                if pd.notna(rsi_val):
                    print(f"❌ RSI={rsi_val:.1f}")
                else:
                    print("❌ RSI=N/A")
                
        except Exception as e:
            print(f"⚠️ 失敗: {e}")
            continue
    
    return pd.DataFrame(results)


def screen_golden_cross(stock_ids: List[str]) -> pd.DataFrame:
    """
    黃金交叉策略：找出短均線上穿長均線的股票
    
    Args:
        stock_ids: 要篩選的股票代號清單
    
    Returns:
        符合條件的股票 DataFrame
    """
    fetcher = TWSEFetcher()
    results = []
    
    for stock_id in stock_ids:
        try:
            print(f"🔍 分析 {stock_id}...", end=" ")
            df = fetcher.get_historical_price(stock_id, months=3)
            
            # 計算均線
            df['ma5'] = calculate_ma(df['close'], 5)
            df['ma20'] = calculate_ma(df['close'], 20)
            
            # 檢查最近兩天
            if len(df) < 2:
                print("❌ 資料不足")
                continue
            
            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            # 黃金交叉：今天 MA5 > MA20 且昨天 MA5 <= MA20
            if (pd.notna(current['ma5']) and pd.notna(current['ma20']) and
                pd.notna(prev['ma5']) and pd.notna(prev['ma20'])):
                
                if current['ma5'] > current['ma20'] and prev['ma5'] <= prev['ma20']:
                    results.append({
                        'stock_id': stock_id,
                        'date': current['date'],
                        'close': current['close'],
                        'volume': current['volume'],
                        'ma5': current['ma5'],
                        'ma20': current['ma20'],
                        'cross_strength': ((current['ma5'] - current['ma20']) / current['ma20'] * 100)
                    })
                    print(f"✅ 黃金交叉!")
                else:
                    print(f"❌ MA5={current['ma5']:.1f}, MA20={current['ma20']:.1f}")
            else:
                print("❌ 均線資料不足")
                
        except Exception as e:
            print(f"⚠️ 失敗: {e}")
            continue
    
    return pd.DataFrame(results)


def screen_momentum(stock_ids: List[str], min_volume: int = 1000) -> pd.DataFrame:
    """
    動能策略：找出連續上漲且成交量放大的股票
    
    Args:
        stock_ids: 要篩選的股票代號清單
        min_volume: 最低成交量 (張)
    
    Returns:
        符合條件的股票 DataFrame
    """
    fetcher = TWSEFetcher()
    results = []
    
    for stock_id in stock_ids:
        try:
            print(f"🔍 分析 {stock_id}...", end=" ")
            df = fetcher.get_historical_price(stock_id, months=2)
            
            if len(df) < 3:
                print("❌ 資料不足")
                continue
            
            # 檢查最近 3 天
            recent = df.tail(3)
            closes = recent['close'].tolist()
            volumes = recent['volume'].tolist()
            
            # 條件：連續上漲 + 量能放大
            if (closes[2] > closes[1] > closes[0] and
                volumes[2] > volumes[1] and
                volumes[2] >= min_volume):
                
                latest = recent.iloc[-1]
                gain_pct = ((closes[2] - closes[0]) / closes[0]) * 100
                
                results.append({
                    'stock_id': stock_id,
                    'date': latest['date'],
                    'close': latest['close'],
                    'volume': latest['volume'],
                    '3day_gain': gain_pct,
                    'volume_ratio': volumes[2] / volumes[1]
                })
                print(f"✅ 3日漲幅 {gain_pct:.2f}%")
            else:
                print("❌ 未符合條件")
                
        except Exception as e:
            print(f"⚠️ 失敗: {e}")
            continue
    
    return pd.DataFrame(results)
