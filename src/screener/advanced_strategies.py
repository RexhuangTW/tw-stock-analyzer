"""進階選股策略"""
from typing import List, Callable
import pandas as pd
import numpy as np
from src.data.fetcher import TWSEFetcher
from src.data.yahoo_fetcher import YahooFetcher
from src.indicators.technical import calculate_ma, calculate_rsi, calculate_bollinger_bands
from src.indicators.advanced import calculate_atr, calculate_obv, calculate_adx


def screen_breakout_with_volume(stock_ids: List[str], 
                                  lookback_days: int = 20,
                                  volume_threshold: float = 1.5) -> pd.DataFrame:
    """
    量價突破策略：突破近期高點 + 成交量放大
    
    Args:
        stock_ids: 股票代號清單
        lookback_days: 回顧天數
        volume_threshold: 成交量放大倍數
    
    Returns:
        符合條件的股票 DataFrame
    """
    fetcher = TWSEFetcher()
    results = []
    
    for stock_id in stock_ids:
        try:
            print(f"🔍 分析 {stock_id}...", end=" ")
            df = fetcher.get_historical_price(stock_id, months=2)
            
            if len(df) < lookback_days + 5:
                print("❌ 資料不足")
                continue
            
            latest = df.iloc[-1]
            prev_df = df.iloc[-(lookback_days+1):-1]
            
            # 突破條件
            resistance = prev_df['high'].max()
            avg_volume = prev_df['volume'].mean()
            
            is_breakout = latest['close'] > resistance
            volume_surge = latest['volume'] > avg_volume * volume_threshold
            
            if is_breakout and volume_surge:
                results.append({
                    'stock_id': stock_id,
                    'date': latest['date'],
                    'close': latest['close'],
                    'resistance': resistance,
                    'breakout_pct': ((latest['close'] - resistance) / resistance * 100),
                    'volume': latest['volume'],
                    'avg_volume': avg_volume,
                    'volume_ratio': latest['volume'] / avg_volume
                })
                print(f"✅ 突破 {resistance:.1f} (+{((latest['close']-resistance)/resistance*100):.1f}%)")
            else:
                print("❌ 未突破")
                
        except Exception as e:
            print(f"⚠️ 失敗: {e}")
            continue
    
    return pd.DataFrame(results)


def screen_bollinger_squeeze(stock_ids: List[str], 
                              bb_period: int = 20,
                              squeeze_threshold: float = 0.02) -> pd.DataFrame:
    """
    布林通道收縮策略：通道寬度收窄,準備突破
    
    Args:
        stock_ids: 股票代號清單
        bb_period: 布林通道週期
        squeeze_threshold: 收縮門檻 (寬度/中線比例)
    
    Returns:
        符合條件的股票 DataFrame
    """
    fetcher = TWSEFetcher()
    results = []
    
    for stock_id in stock_ids:
        try:
            print(f"🔍 分析 {stock_id}...", end=" ")
            df = fetcher.get_historical_price(stock_id, months=2)
            
            # 計算布林通道
            bb_df = calculate_bollinger_bands(df['close'], period=bb_period, std_dev=2.0)
            df = df.join(bb_df)
            
            latest = df.iloc[-1]
            
            # 通道寬度
            bandwidth = (latest['upper'] - latest['lower']) / latest['middle']
            
            if bandwidth < squeeze_threshold:
                # 計算 ATR 判斷波動性
                atr = calculate_atr(df['high'], df['low'], df['close']).iloc[-1]
                
                results.append({
                    'stock_id': stock_id,
                    'date': latest['date'],
                    'close': latest['close'],
                    'bb_middle': latest['middle'],
                    'bb_upper': latest['upper'],
                    'bb_lower': latest['lower'],
                    'bandwidth': bandwidth,
                    'atr': atr,
                    'position': 'UPPER' if latest['close'] > latest['middle'] else 'LOWER'
                })
                print(f"✅ 收縮 ({bandwidth*100:.2f}%)")
            else:
                print(f"❌ 通道寬 ({bandwidth*100:.2f}%)")
                
        except Exception as e:
            print(f"⚠️ 失敗: {e}")
            continue
    
    return pd.DataFrame(results)


def screen_obv_divergence(stock_ids: List[str], lookback_days: int = 30) -> pd.DataFrame:
    """
    OBV 背離策略：價格與能量潮背離
    
    Args:
        stock_ids: 股票代號清單
        lookback_days: 回顧天數
    
    Returns:
        符合條件的股票 DataFrame
    """
    fetcher = TWSEFetcher()
    results = []
    
    for stock_id in stock_ids:
        try:
            print(f"🔍 分析 {stock_id}...", end=" ")
            df = fetcher.get_historical_price(stock_id, months=2)
            
            # 計算 OBV
            df['obv'] = calculate_obv(df['close'], df['volume'])
            
            recent_df = df.tail(lookback_days)
            
            # 價格趨勢
            price_slope = np.polyfit(range(len(recent_df)), recent_df['close'], 1)[0]
            
            # OBV 趨勢
            obv_slope = np.polyfit(range(len(recent_df)), recent_df['obv'], 1)[0]
            
            # 背離：價格向上但 OBV 向下 (看跌背離)
            # 或價格向下但 OBV 向上 (看漲背離)
            if (price_slope > 0 and obv_slope < 0) or (price_slope < 0 and obv_slope > 0):
                divergence_type = 'BEARISH' if price_slope > 0 else 'BULLISH'
                
                latest = df.iloc[-1]
                
                results.append({
                    'stock_id': stock_id,
                    'date': latest['date'],
                    'close': latest['close'],
                    'obv': latest['obv'],
                    'divergence': divergence_type,
                    'price_slope': price_slope,
                    'obv_slope': obv_slope
                })
                print(f"✅ {divergence_type} 背離")
            else:
                print("❌ 無背離")
                
        except Exception as e:
            print(f"⚠️ 失敗: {e}")
            continue
    
    return pd.DataFrame(results)


def screen_multi_factor(stock_ids: List[str],
                        weights: dict = None,
                        min_score: float = 0) -> pd.DataFrame:
    """
    多因子選股：綜合技術面評分
    
    Args:
        stock_ids: 股票代號清單
        weights: 各因子權重,預設均等
        min_score: 最低分數門檻 (0-100)
    
    Returns:
        帶評分的股票 DataFrame
    """
    if weights is None:
        weights = {
            'trend': 0.3,      # 趨勢分數
            'momentum': 0.3,   # 動能分數
            'volatility': 0.2, # 波動性分數
            'volume': 0.2      # 成交量分數
        }
    
    fetcher = TWSEFetcher()
    results = []
    
    for stock_id in stock_ids:
        try:
            print(f"🔍 分析 {stock_id}...", end=" ")
            df = fetcher.get_historical_price(stock_id, months=3)
            
            # 計算指標
            df['ma20'] = calculate_ma(df['close'], 20)
            df['ma60'] = calculate_ma(df['close'], 60)
            df['rsi'] = calculate_rsi(df['close'], 14)
            adx_df = calculate_adx(df['high'], df['low'], df['close'])
            df = df.join(adx_df)
            
            latest = df.iloc[-1]
            
            # 1. 趨勢分數 (0-10)
            trend_score = 0
            if pd.notna(latest['ma20']) and pd.notna(latest['ma60']):
                if latest['close'] > latest['ma20'] > latest['ma60']:
                    trend_score = 10
                elif latest['close'] > latest['ma20']:
                    trend_score = 7
                elif latest['close'] > latest['ma60']:
                    trend_score = 5
                else:
                    trend_score = 2
            
            # 2. 動能分數 (0-10)
            momentum_score = 0
            if pd.notna(latest['rsi']):
                if 50 < latest['rsi'] < 70:
                    momentum_score = 10
                elif 40 < latest['rsi'] < 50:
                    momentum_score = 7
                elif latest['rsi'] < 30:
                    momentum_score = 5  # 超賣,潛在反彈
                else:
                    momentum_score = 3
            
            # 3. 波動性分數 (0-10)
            volatility_score = 0
            if pd.notna(latest['adx']):
                if latest['adx'] > 25:
                    volatility_score = 10  # 趨勢強
                elif latest['adx'] > 20:
                    volatility_score = 7
                else:
                    volatility_score = 4  # 盤整
            
            # 4. 成交量分數 (0-10)
            avg_volume_20 = df['volume'].tail(20).mean()
            volume_ratio = latest['volume'] / avg_volume_20
            volume_score = min(10, volume_ratio * 5)
            
            # 綜合評分
            total_score = (
                trend_score * weights['trend'] +
                momentum_score * weights['momentum'] +
                volatility_score * weights['volatility'] +
                volume_score * weights['volume']
            ) * 10  # 轉換為百分制
            
            results.append({
                'stock_id': stock_id,
                'date': latest['date'],
                'close': latest['close'],
                'total_score': round(total_score, 2),
                'trend_score': trend_score,
                'momentum_score': momentum_score,
                'volatility_score': volatility_score,
                'volume_score': round(volume_score, 2),
                'rsi': round(latest['rsi'], 2) if pd.notna(latest['rsi']) else None,
                'adx': round(latest['adx'], 2) if pd.notna(latest['adx']) else None
            })
            print(f"✅ 評分 {total_score:.1f}")
                
        except Exception as e:
            print(f"⚠️ 失敗: {e}")
            continue
    
    df_result = pd.DataFrame(results)
    
    # 篩選分數達標的股票
    if not df_result.empty and min_score > 0:
        df_result = df_result[df_result['total_score'] >= min_score]
    
    # 按評分排序
    if not df_result.empty:
        df_result = df_result.sort_values('total_score', ascending=False)
    
    return df_result
