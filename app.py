#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

# 在所有其他 import 之前設定路徑
_project_root = Path(__file__).parent.absolute()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

"""台股分析器 Streamlit Web UI"""
import streamlit as st
import pandas as pd
from datetime import datetime

# 頁面配置
st.set_page_config(
    page_title="台股分析器",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 側邊欄
st.sidebar.title("🦞 台股分析器")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "選擇功能",
    ["📊 K線圖", "🔍 選股策略", "🔄 策略回測", "📈 技術指標", "⚙️ 設定"]
)

st.sidebar.markdown("---")
st.sidebar.info("v1.5 | 2026-03-17")

# 主頁面
if page == "📊 K線圖":
    st.title("📊 互動式 K 線圖")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        stock_id = st.text_input("股票代號", value="2330", help="輸入台股代號 (e.g., 2330)")
    
    with col2:
        data_source = st.selectbox("資料來源", ["TWSE", "Yahoo Finance"])
    
    with col3:
        period = st.selectbox("時間範圍", ["1個月", "3個月", "6個月", "1年"])
    
    if st.button("🔍 分析", type="primary"):
        with st.spinner("正在擷取資料..."):
            try:
                if data_source == "TWSE":
                    from src.data.fetcher import TWSEFetcher
                    fetcher = TWSEFetcher()
                    
                    period_map = {"1個月": 1, "3個月": 3, "6個月": 6, "1年": 12}
                    df = fetcher.get_historical_price(stock_id, months=period_map[period])
                else:
                    from src.data.yahoo_fetcher import YahooFetcher
                    fetcher = YahooFetcher()
                    
                    period_map = {"1個月": "1mo", "3個月": "3mo", "6個月": "6mo", "1年": "1y"}
                    symbol = f"{stock_id}.TW"
                    df = fetcher.get_stock_data(symbol, period=period_map[period])
                
                # 計算技術指標
                from src.indicators.technical import calculate_ma, calculate_rsi, calculate_macd
                
                df['ma5'] = calculate_ma(df['close'], 5)
                df['ma20'] = calculate_ma(df['close'], 20)
                df['rsi'] = calculate_rsi(df['close'], 14)
                macd_df = calculate_macd(df['close'])
                df = df.join(macd_df)
                
                # 顯示最新資訊
                latest = df.iloc[-1]
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("收盤價", f"${latest['close']:.2f}", f"{latest['close'] - df.iloc[-2]['close']:.2f}")
                col2.metric("成交量", f"{latest['volume']:,} 張")
                col3.metric("RSI(14)", f"{latest['rsi']:.1f}" if pd.notna(latest['rsi']) else "N/A")
                col4.metric("MA5/MA20", f"{latest['ma5']:.1f}/{latest['ma20']:.1f}" if pd.notna(latest['ma5']) else "N/A")
                
                # 繪製圖表
                from src.visualization.plotly_charts import create_candlestick_chart, create_technical_chart
                
                st.subheader("K 線圖")
                fig1 = create_candlestick_chart(
                    df,
                    title=f"{stock_id} K線圖",
                    show_volume=True,
                    indicators={'MA5': df['ma5'], 'MA20': df['ma20']}
                )
                st.plotly_chart(fig1, use_container_width=True)
                
                st.subheader("技術指標")
                fig2 = create_technical_chart(
                    df,
                    rsi=df['rsi'],
                    macd=df[['macd', 'signal', 'histogram']],
                    title=f"{stock_id} 技術指標"
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # 資料表
                with st.expander("📋 查看原始資料"):
                    st.dataframe(df.tail(20), use_container_width=True)
                
                st.success("✅ 分析完成!")
                
            except Exception as e:
                st.error(f"❌ 錯誤: {e}")

elif page == "🔍 選股策略":
    st.title("🔍 選股策略")
    
    strategy = st.selectbox(
        "選擇策略",
        ["RSI 超賣", "黃金交叉", "動能策略", "量價突破", "布林收縮", "OBV背離", "多因子評分"]
    )
    
    stock_list = st.text_area(
        "股票清單 (逗號分隔)",
        value="2330,2317,2454,2412,2308",
        help="輸入要篩選的股票代號,用逗號分隔"
    )
    
    if st.button("🚀 執行選股", type="primary"):
        stock_ids = [s.strip() for s in stock_list.split(",")]
        
        with st.spinner(f"正在分析 {len(stock_ids)} 檔股票..."):
            try:
                if strategy == "RSI 超賣":
                    from src.screener.strategies import screen_rsi_oversold
                    result = screen_rsi_oversold(stock_ids, rsi_threshold=30)
                
                elif strategy == "黃金交叉":
                    from src.screener.strategies import screen_golden_cross
                    result = screen_golden_cross(stock_ids)
                
                elif strategy == "動能策略":
                    from src.screener.strategies import screen_momentum
                    result = screen_momentum(stock_ids)
                
                elif strategy == "量價突破":
                    from src.screener.advanced_strategies import screen_breakout_with_volume
                    result = screen_breakout_with_volume(stock_ids)
                
                elif strategy == "布林收縮":
                    from src.screener.advanced_strategies import screen_bollinger_squeeze
                    result = screen_bollinger_squeeze(stock_ids)
                
                elif strategy == "OBV背離":
                    from src.screener.advanced_strategies import screen_obv_divergence
                    result = screen_obv_divergence(stock_ids)
                
                elif strategy == "多因子評分":
                    from src.screener.advanced_strategies import screen_multi_factor
                    result = screen_multi_factor(stock_ids)
                
                if result.empty:
                    st.warning("⚠️ 無符合條件的股票")
                else:
                    st.success(f"✅ 找到 {len(result)} 檔符合條件的股票")
                    st.dataframe(result, use_container_width=True)
                    
                    # 下載按鈕
                    csv = result.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        "📥 下載結果 (CSV)",
                        csv,
                        f"screening_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )
                
            except Exception as e:
                st.error(f"❌ 錯誤: {e}")

elif page == "🔄 策略回測":
    st.title("🔄 策略回測")
    
    col1, col2 = st.columns(2)
    
    with col1:
        stock_id = st.text_input("股票代號", value="2330")
    
    with col2:
        initial_capital = st.number_input("初始資金", value=1000000, step=100000)
    
    strategy = st.selectbox("選擇策略", ["均線交叉 (MA5 x MA20)", "RSI 策略"])
    
    if st.button("🚀 執行回測", type="primary"):
        with st.spinner("正在回測..."):
            try:
                from src.data.fetcher import TWSEFetcher
                from src.backtest.engine import BacktestEngine, sma_crossover_strategy, rsi_strategy
                
                # 取得資料
                fetcher = TWSEFetcher()
                df = fetcher.get_historical_price(stock_id, months=6)
                
                # 執行回測
                engine = BacktestEngine(initial_capital=initial_capital)
                
                if strategy == "均線交叉 (MA5 x MA20)":
                    strat = sma_crossover_strategy(5, 20)
                else:
                    strat = rsi_strategy(14, 30, 70)
                
                result = engine.run(df, strat)
                
                # 顯示結果
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("最終淨值", f"${result['final_equity']:,.0f}")
                col2.metric("總報酬率", f"{result['total_return_pct']:.2f}%")
                col3.metric("最大回撤", f"{result['max_drawdown_pct']:.2f}%")
                col4.metric("勝率", f"{result['win_rate_pct']:.1f}%")
                
                st.metric("交易次數", result['total_trades'])
                
                # 回測圖表
                from src.visualization.plotly_charts import create_backtest_chart
                
                fig = create_backtest_chart(
                    result['equity_curve'],
                    result['trades'],
                    title=f"{stock_id} 回測結果 - {strategy}"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 交易紀錄
                with st.expander("📋 查看交易紀錄"):
                    if not result['trades'].empty:
                        st.dataframe(result['trades'], use_container_width=True)
                    else:
                        st.info("無交易紀錄")
                
            except Exception as e:
                st.error(f"❌ 錯誤: {e}")

elif page == "📈 技術指標":
    st.title("📈 技術指標計算器")
    
    stock_id = st.text_input("股票代號", value="2330")
    
    indicators = st.multiselect(
        "選擇指標",
        ["MA", "RSI", "MACD", "KD", "布林通道", "ATR", "OBV", "ADX"],
        default=["MA", "RSI", "MACD"]
    )
    
    if st.button("📊 計算", type="primary"):
        with st.spinner("正在計算..."):
            try:
                from src.data.fetcher import TWSEFetcher
                fetcher = TWSEFetcher()
                df = fetcher.get_historical_price(stock_id, months=3)
                
                results = {}
                
                if "MA" in indicators:
                    from src.indicators.technical import calculate_ma
                    df['ma5'] = calculate_ma(df['close'], 5)
                    df['ma20'] = calculate_ma(df['close'], 20)
                    results['MA5'] = df['ma5'].iloc[-1]
                    results['MA20'] = df['ma20'].iloc[-1]
                
                if "RSI" in indicators:
                    from src.indicators.technical import calculate_rsi
                    df['rsi'] = calculate_rsi(df['close'], 14)
                    results['RSI(14)'] = df['rsi'].iloc[-1]
                
                if "MACD" in indicators:
                    from src.indicators.technical import calculate_macd
                    macd_df = calculate_macd(df['close'])
                    results['MACD'] = macd_df['macd'].iloc[-1]
                    results['Signal'] = macd_df['signal'].iloc[-1]
                
                if "ATR" in indicators:
                    from src.indicators.advanced import calculate_atr
                    atr = calculate_atr(df['high'], df['low'], df['close'])
                    results['ATR(14)'] = atr.iloc[-1]
                
                if "OBV" in indicators:
                    from src.indicators.advanced import calculate_obv
                    obv = calculate_obv(df['close'], df['volume'])
                    results['OBV'] = obv.iloc[-1]
                
                if "ADX" in indicators:
                    from src.indicators.advanced import calculate_adx
                    adx_df = calculate_adx(df['high'], df['low'], df['close'])
                    results['ADX'] = adx_df['adx'].iloc[-1]
                
                # 顯示結果
                st.subheader("計算結果")
                
                cols = st.columns(min(4, len(results)))
                for idx, (name, value) in enumerate(results.items()):
                    with cols[idx % 4]:
                        st.metric(name, f"{value:.2f}" if pd.notna(value) else "N/A")
                
                # 完整資料表
                with st.expander("📊 查看完整資料"):
                    st.dataframe(df.tail(20), use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ 錯誤: {e}")

elif page == "⚙️ 設定":
    st.title("⚙️ 系統設定")
    
    st.subheader("通知設定")
    
    enable_discord = st.checkbox("啟用 Discord 通知")
    if enable_discord:
        discord_webhook = st.text_input("Discord Webhook URL", type="password")
    
    enable_telegram = st.checkbox("啟用 Telegram 通知")
    if enable_telegram:
        telegram_token = st.text_input("Telegram Bot Token", type="password")
        telegram_chat_id = st.text_input("Telegram Chat ID")
    
    st.markdown("---")
    
    st.subheader("快取設定")
    cache_ttl = st.slider("快取有效期限 (小時)", 1, 48, 24)
    
    if st.button("清空快取"):
        from src.data.cache import _cache
        _cache.clear()
        st.success("✅ 快取已清空")
    
    st.markdown("---")
    
    st.subheader("關於")
    st.info("""
    **台股分析器 v1.5**
    
    - 資料來源: TWSE + Yahoo Finance
    - 技術指標: 15+ 種
    - 選股策略: 8 種
    - 回測引擎: 完整支援
    - 視覺化: 互動式圖表
    
    開發者: Claw-Agent 🦞
    """)
