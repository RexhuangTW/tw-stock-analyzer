"""Plotly 互動式圖表"""
import pandas as pd
from typing import Optional, List
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_candlestick_chart(
    data: pd.DataFrame,
    title: str = "K線圖",
    show_volume: bool = True,
    indicators: Optional[dict] = None
) -> go.Figure:
    """
    建立互動式 K 線圖
    
    Args:
        data: 包含 date, open, high, low, close, volume 的 DataFrame
        title: 圖表標題
        show_volume: 是否顯示成交量
        indicators: 技術指標 dict, e.g., {'ma5': data['ma5'], 'ma20': data['ma20']}
    
    Returns:
        Plotly Figure 物件
    """
    # 建立子圖
    rows = 2 if show_volume else 1
    specs = [[{"secondary_y": False}], [{"secondary_y": False}]] if show_volume else [[{"secondary_y": False}]]
    
    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(title, "成交量") if show_volume else (title,),
        row_heights=[0.7, 0.3] if show_volume else [1.0]
    )
    
    # K 線圖
    fig.add_trace(
        go.Candlestick(
            x=data['date'],
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='K線',
            increasing_line_color='red',
            decreasing_line_color='green'
        ),
        row=1, col=1
    )
    
    # 技術指標
    if indicators:
        colors = ['blue', 'orange', 'purple', 'brown']
        for idx, (name, values) in enumerate(indicators.items()):
            fig.add_trace(
                go.Scatter(
                    x=data['date'],
                    y=values,
                    name=name.upper(),
                    line=dict(color=colors[idx % len(colors)], width=1.5),
                    opacity=0.7
                ),
                row=1, col=1
            )
    
    # 成交量
    if show_volume:
        colors = ['red' if data.iloc[i]['close'] >= data.iloc[i]['open'] else 'green'
                  for i in range(len(data))]
        
        fig.add_trace(
            go.Bar(
                x=data['date'],
                y=data['volume'],
                name='成交量',
                marker_color=colors,
                opacity=0.6
            ),
            row=2, col=1
        )
    
    # 更新佈局
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_white',
        height=600 if show_volume else 400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(title_text="日期", row=rows, col=1)
    fig.update_yaxes(title_text="價格 (元)", row=1, col=1)
    if show_volume:
        fig.update_yaxes(title_text="成交量 (張)", row=2, col=1)
    
    return fig


def create_technical_chart(
    data: pd.DataFrame,
    rsi: Optional[pd.Series] = None,
    macd: Optional[pd.DataFrame] = None,
    title: str = "技術指標"
) -> go.Figure:
    """
    建立技術指標圖表
    
    Args:
        data: 價格資料
        rsi: RSI 資料
        macd: MACD 資料 (需包含 macd, signal, histogram 欄位)
        title: 標題
    
    Returns:
        Plotly Figure
    """
    rows = 1
    if rsi is not None:
        rows += 1
    if macd is not None:
        rows += 1
    
    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5] + [0.25] * (rows - 1)
    )
    
    # 價格線
    fig.add_trace(
        go.Scatter(
            x=data['date'],
            y=data['close'],
            name='收盤價',
            line=dict(color='black', width=2)
        ),
        row=1, col=1
    )
    
    current_row = 2
    
    # RSI
    if rsi is not None:
        fig.add_trace(
            go.Scatter(
                x=data['date'],
                y=rsi,
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=current_row, col=1
        )
        
        # 超買超賣線
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=current_row, col=1)
        fig.add_hrect(y0=30, y1=70, fillcolor="gray", opacity=0.1, row=current_row, col=1)
        
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=current_row, col=1)
        current_row += 1
    
    # MACD
    if macd is not None:
        fig.add_trace(
            go.Scatter(
                x=data['date'],
                y=macd['macd'],
                name='MACD',
                line=dict(color='blue', width=2)
            ),
            row=current_row, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data['date'],
                y=macd['signal'],
                name='Signal',
                line=dict(color='orange', width=2)
            ),
            row=current_row, col=1
        )
        
        colors = ['red' if x > 0 else 'green' for x in macd['histogram']]
        fig.add_trace(
            go.Bar(
                x=data['date'],
                y=macd['histogram'],
                name='Histogram',
                marker_color=colors,
                opacity=0.4
            ),
            row=current_row, col=1
        )
        
        fig.update_yaxes(title_text="MACD", row=current_row, col=1)
    
    # 更新佈局
    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_white',
        height=200 * rows,
        showlegend=True
    )
    
    return fig


def create_backtest_chart(
    equity_curve: pd.DataFrame,
    trades: Optional[pd.DataFrame] = None,
    title: str = "回測結果"
) -> go.Figure:
    """
    建立回測結果互動圖表
    
    Args:
        equity_curve: 淨值曲線
        trades: 交易紀錄
        title: 標題
    
    Returns:
        Plotly Figure
    """
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("淨值曲線", "累積報酬率", "回撤"),
        row_heights=[0.5, 0.25, 0.25]
    )
    
    # 淨值曲線
    fig.add_trace(
        go.Scatter(
            x=equity_curve['date'],
            y=equity_curve['total_equity'],
            name='總淨值',
            line=dict(color='blue', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 100, 255, 0.1)'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=equity_curve['date'],
            y=equity_curve['peak'],
            name='歷史高點',
            line=dict(color='red', width=1, dash='dash'),
            opacity=0.5
        ),
        row=1, col=1
    )
    
    # 買賣點標記
    if trades is not None and not trades.empty:
        buy_trades = trades[trades['action'] == 'BUY']
        sell_trades = trades[trades['action'] == 'SELL']
        
        if not buy_trades.empty:
            fig.add_trace(
                go.Scatter(
                    x=buy_trades['date'],
                    y=[equity_curve[equity_curve['date'] == d]['total_equity'].values[0]
                       for d in buy_trades['date']],
                    mode='markers',
                    name='買入',
                    marker=dict(symbol='triangle-up', size=12, color='red'),
                    hovertext=[f"買入 {row['shares']} 張 @ {row['price']}" for _, row in buy_trades.iterrows()]
                ),
                row=1, col=1
            )
        
        if not sell_trades.empty:
            fig.add_trace(
                go.Scatter(
                    x=sell_trades['date'],
                    y=[equity_curve[equity_curve['date'] == d]['total_equity'].values[0]
                       for d in sell_trades['date']],
                    mode='markers',
                    name='賣出',
                    marker=dict(symbol='triangle-down', size=12, color='green'),
                    hovertext=[f"賣出 {row['shares']} 張 @ {row['price']}" for _, row in sell_trades.iterrows()]
                ),
                row=1, col=1
            )
    
    # 累積報酬率
    fig.add_trace(
        go.Scatter(
            x=equity_curve['date'],
            y=equity_curve['returns'] * 100,
            name='報酬率',
            line=dict(color='green', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 200, 100, 0.1)'
        ),
        row=2, col=1
    )
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.3, row=2, col=1)
    
    # 回撤
    fig.add_trace(
        go.Scatter(
            x=equity_curve['date'],
            y=equity_curve['drawdown'] * 100,
            name='回撤',
            line=dict(color='red', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.2)'
        ),
        row=3, col=1
    )
    
    # 更新佈局
    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_white',
        height=800,
        showlegend=True
    )
    
    fig.update_yaxes(title_text="淨值 (元)", row=1, col=1)
    fig.update_yaxes(title_text="報酬率 (%)", row=2, col=1)
    fig.update_yaxes(title_text="回撤 (%)", row=3, col=1)
    fig.update_xaxes(title_text="日期", row=3, col=1)
    
    return fig
