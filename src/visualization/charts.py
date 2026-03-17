"""圖表視覺化"""
import pandas as pd
import numpy as np
from typing import Optional, List
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure


# 設定中文字型 (macOS)
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


def plot_candlestick(data: pd.DataFrame, 
                     title: str = "K線圖",
                     save_path: Optional[str] = None,
                     show_volume: bool = True,
                     figsize: tuple = (14, 8)) -> Figure:
    """
    繪製 K 線圖
    
    Args:
        data: 包含 date, open, high, low, close, volume 的 DataFrame
        title: 圖表標題
        save_path: 儲存路徑 (None = 不儲存)
        show_volume: 是否顯示成交量
        figsize: 圖表尺寸
    
    Returns:
        matplotlib Figure
    """
    fig, axes = plt.subplots(2 if show_volume else 1, 1, 
                             figsize=figsize,
                             gridspec_kw={'height_ratios': [3, 1]} if show_volume else None)
    
    if not show_volume:
        axes = [axes]
    
    ax_price = axes[0]
    
    # 處理日期
    data = data.copy()
    data['date_num'] = mdates.date2num(pd.to_datetime(data['date']))
    
    # 繪製 K 線
    for idx, row in data.iterrows():
        color = 'red' if row['close'] >= row['open'] else 'green'
        
        # 實體
        ax_price.plot([row['date_num'], row['date_num']], 
                     [row['open'], row['close']], 
                     color=color, linewidth=6, solid_capstyle='round')
        
        # 影線
        ax_price.plot([row['date_num'], row['date_num']], 
                     [row['low'], row['high']], 
                     color=color, linewidth=1)
    
    ax_price.set_title(title, fontsize=16, fontweight='bold')
    ax_price.set_ylabel('價格 (元)', fontsize=12)
    ax_price.grid(True, alpha=0.3)
    ax_price.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    
    # 成交量
    if show_volume:
        ax_vol = axes[1]
        colors = ['red' if data.iloc[i]['close'] >= data.iloc[i]['open'] else 'green' 
                  for i in range(len(data))]
        ax_vol.bar(data['date_num'], data['volume'], color=colors, alpha=0.6)
        ax_vol.set_ylabel('成交量 (張)', fontsize=12)
        ax_vol.grid(True, alpha=0.3)
        ax_vol.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 圖表已儲存: {save_path}")
    
    return fig


def plot_technical_indicators(data: pd.DataFrame,
                               indicators: List[str],
                               title: str = "技術指標",
                               save_path: Optional[str] = None,
                               figsize: tuple = (14, 10)) -> Figure:
    """
    繪製技術指標圖
    
    Args:
        data: 包含價格與指標的 DataFrame
        indicators: 要顯示的指標欄位名稱 (e.g., ['ma5', 'ma20', 'rsi'])
        title: 圖表標題
        save_path: 儲存路徑
        figsize: 圖表尺寸
    
    Returns:
        matplotlib Figure
    """
    fig, axes = plt.subplots(3, 1, figsize=figsize, 
                            gridspec_kw={'height_ratios': [2, 1, 1]})
    
    data = data.copy()
    data['date'] = pd.to_datetime(data['date'])
    
    # 價格 + 均線
    ax_price = axes[0]
    ax_price.plot(data['date'], data['close'], label='收盤價', linewidth=2, color='black')
    
    for indicator in indicators:
        if indicator in data.columns and indicator.startswith('ma'):
            ax_price.plot(data['date'], data[indicator], 
                         label=indicator.upper(), linewidth=1.5, alpha=0.8)
    
    ax_price.set_title(title, fontsize=16, fontweight='bold')
    ax_price.set_ylabel('價格 (元)', fontsize=12)
    ax_price.legend(loc='best')
    ax_price.grid(True, alpha=0.3)
    
    # RSI
    ax_rsi = axes[1]
    if 'rsi' in data.columns:
        ax_rsi.plot(data['date'], data['rsi'], label='RSI(14)', linewidth=2, color='purple')
        ax_rsi.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='超買(70)')
        ax_rsi.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='超賣(30)')
        ax_rsi.fill_between(data['date'], 30, 70, alpha=0.1, color='gray')
        ax_rsi.set_ylim(0, 100)
        ax_rsi.set_ylabel('RSI', fontsize=12)
        ax_rsi.legend(loc='best')
        ax_rsi.grid(True, alpha=0.3)
    
    # MACD
    ax_macd = axes[2]
    if 'macd' in data.columns and 'signal' in data.columns:
        ax_macd.plot(data['date'], data['macd'], label='MACD', linewidth=2, color='blue')
        ax_macd.plot(data['date'], data['signal'], label='Signal', linewidth=2, color='orange')
        
        if 'histogram' in data.columns:
            colors = ['red' if x > 0 else 'green' for x in data['histogram']]
            ax_macd.bar(data['date'], data['histogram'], label='Histogram', 
                       color=colors, alpha=0.3, width=0.8)
        
        ax_macd.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax_macd.set_ylabel('MACD', fontsize=12)
        ax_macd.legend(loc='best')
        ax_macd.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 圖表已儲存: {save_path}")
    
    return fig


def plot_backtest_results(equity_curve: pd.DataFrame,
                          trades: pd.DataFrame,
                          title: str = "回測結果",
                          save_path: Optional[str] = None,
                          figsize: tuple = (14, 10)) -> Figure:
    """
    繪製回測結果
    
    Args:
        equity_curve: 淨值曲線 DataFrame
        trades: 交易紀錄 DataFrame
        title: 圖表標題
        save_path: 儲存路徑
        figsize: 圖表尺寸
    
    Returns:
        matplotlib Figure
    """
    fig, axes = plt.subplots(3, 1, figsize=figsize,
                            gridspec_kw={'height_ratios': [2, 1, 1]})
    
    equity_curve['date'] = pd.to_datetime(equity_curve['date'])
    
    # 淨值曲線
    ax_equity = axes[0]
    ax_equity.plot(equity_curve['date'], equity_curve['total_equity'], 
                  linewidth=2, color='blue', label='總淨值')
    ax_equity.plot(equity_curve['date'], equity_curve['peak'], 
                  linewidth=1, color='red', linestyle='--', alpha=0.5, label='歷史高點')
    
    # 標記買賣點
    if not trades.empty:
        trades['date'] = pd.to_datetime(trades['date'])
        buy_trades = trades[trades['action'] == 'BUY']
        sell_trades = trades[trades['action'] == 'SELL']
        
        for _, trade in buy_trades.iterrows():
            equity_at_trade = equity_curve[equity_curve['date'] == trade['date']]['total_equity'].values
            if len(equity_at_trade) > 0:
                ax_equity.scatter(trade['date'], equity_at_trade[0], 
                                marker='^', color='red', s=100, zorder=5)
        
        for _, trade in sell_trades.iterrows():
            equity_at_trade = equity_curve[equity_curve['date'] == trade['date']]['total_equity'].values
            if len(equity_at_trade) > 0:
                ax_equity.scatter(trade['date'], equity_at_trade[0], 
                                marker='v', color='green', s=100, zorder=5)
    
    ax_equity.set_title(title, fontsize=16, fontweight='bold')
    ax_equity.set_ylabel('淨值 (元)', fontsize=12)
    ax_equity.legend(loc='best')
    ax_equity.grid(True, alpha=0.3)
    
    # 報酬率
    ax_returns = axes[1]
    ax_returns.plot(equity_curve['date'], equity_curve['returns'] * 100, 
                   linewidth=2, color='green', label='累積報酬率')
    ax_returns.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax_returns.set_ylabel('報酬率 (%)', fontsize=12)
    ax_returns.legend(loc='best')
    ax_returns.grid(True, alpha=0.3)
    
    # 回撤
    ax_drawdown = axes[2]
    ax_drawdown.fill_between(equity_curve['date'], 
                            equity_curve['drawdown'] * 100, 0,
                            color='red', alpha=0.3, label='回撤')
    ax_drawdown.set_ylabel('回撤 (%)', fontsize=12)
    ax_drawdown.legend(loc='best')
    ax_drawdown.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 圖表已儲存: {save_path}")
    
    return fig


def plot_screener_results(results: pd.DataFrame,
                         metric: str = 'rsi',
                         title: str = "選股結果",
                         save_path: Optional[str] = None,
                         figsize: tuple = (12, 6)) -> Figure:
    """
    繪製選股結果圖表
    
    Args:
        results: 選股結果 DataFrame
        metric: 要視覺化的指標欄位
        title: 圖表標題
        save_path: 儲存路徑
        figsize: 圖表尺寸
    
    Returns:
        matplotlib Figure
    """
    if results.empty:
        print("❌ 無資料可繪製")
        return None
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # 橫條圖
    ax.barh(results['stock_id'], results[metric], color='steelblue', alpha=0.7)
    ax.set_xlabel(metric.upper(), fontsize=12)
    ax.set_ylabel('股票代號', fontsize=12)
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 圖表已儲存: {save_path}")
    
    return fig
