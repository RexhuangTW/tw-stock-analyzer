"""回測引擎"""
from typing import Callable, Optional, Dict, List
import pandas as pd
import numpy as np
from datetime import datetime


class BacktestEngine:
    """策略回測引擎"""
    
    def __init__(self, 
                 initial_capital: float = 1000000,
                 commission_rate: float = 0.001425,
                 tax_rate: float = 0.003):
        """
        Args:
            initial_capital: 初始資金
            commission_rate: 手續費率 (預設 0.1425%)
            tax_rate: 證交稅 (預設 0.3%，賣出時收)
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.tax_rate = tax_rate
        
        self.reset()
    
    def reset(self):
        """重置回測狀態"""
        self.cash = self.initial_capital
        self.position = 0  # 持股張數
        self.trades: List[Dict] = []  # 交易紀錄
        self.equity_curve: List[Dict] = []  # 淨值曲線
    
    def _calculate_cost(self, price: float, shares: int, is_buy: bool) -> float:
        """
        計算交易成本
        
        Args:
            price: 成交價
            shares: 張數
            is_buy: 是否為買入
        
        Returns:
            總成本 (含手續費與稅)
        """
        amount = price * shares * 1000  # 1張 = 1000股
        commission = amount * self.commission_rate
        
        if is_buy:
            return amount + commission
        else:
            tax = amount * self.tax_rate
            return amount - commission - tax
    
    def buy(self, date: pd.Timestamp, price: float, shares: int) -> bool:
        """
        買入
        
        Args:
            date: 交易日期
            price: 買入價
            shares: 買入張數
        
        Returns:
            是否成功
        """
        cost = self._calculate_cost(price, shares, is_buy=True)
        
        if cost > self.cash:
            return False
        
        self.cash -= cost
        self.position += shares
        
        self.trades.append({
            'date': date,
            'action': 'BUY',
            'price': price,
            'shares': shares,
            'cost': cost,
            'cash': self.cash,
            'position': self.position
        })
        
        return True
    
    def sell(self, date: pd.Timestamp, price: float, shares: int) -> bool:
        """
        賣出
        
        Args:
            date: 交易日期
            price: 賣出價
            shares: 賣出張數
        
        Returns:
            是否成功
        """
        if shares > self.position:
            return False
        
        proceeds = self._calculate_cost(price, shares, is_buy=False)
        
        self.cash += proceeds
        self.position -= shares
        
        self.trades.append({
            'date': date,
            'action': 'SELL',
            'price': price,
            'shares': shares,
            'proceeds': proceeds,
            'cash': self.cash,
            'position': self.position
        })
        
        return True
    
    def update_equity(self, date: pd.Timestamp, current_price: float):
        """
        更新淨值曲線
        
        Args:
            date: 日期
            current_price: 當前股價
        """
        market_value = self.position * current_price * 1000
        total_equity = self.cash + market_value
        
        self.equity_curve.append({
            'date': date,
            'cash': self.cash,
            'position': self.position,
            'market_value': market_value,
            'total_equity': total_equity,
            'returns': (total_equity - self.initial_capital) / self.initial_capital
        })
    
    def run(self, 
            data: pd.DataFrame,
            strategy: Callable[[pd.DataFrame, int], str]) -> Dict:
        """
        執行回測
        
        Args:
            data: 歷史資料 DataFrame (需包含 date, close 等欄位)
            strategy: 策略函數，接收 (data, current_index)，回傳 'BUY'/'SELL'/'HOLD'
        
        Returns:
            回測結果統計
        """
        self.reset()
        
        for i in range(len(data)):
            current = data.iloc[i]
            signal = strategy(data, i)
            
            if signal == 'BUY' and self.position == 0:
                # 全部資金買入
                max_shares = int(self.cash / (current['close'] * 1000 * (1 + self.commission_rate)))
                if max_shares > 0:
                    self.buy(current['date'], current['close'], max_shares)
            
            elif signal == 'SELL' and self.position > 0:
                # 全部賣出
                self.sell(current['date'], current['close'], self.position)
            
            # 更新淨值
            self.update_equity(current['date'], current['close'])
        
        # 計算統計數據
        return self.calculate_statistics()
    
    def calculate_statistics(self) -> Dict:
        """計算回測統計數據"""
        if not self.equity_curve:
            return {}
        
        equity_df = pd.DataFrame(self.equity_curve)
        trades_df = pd.DataFrame(self.trades) if self.trades else pd.DataFrame()
        
        final_equity = equity_df['total_equity'].iloc[-1]
        total_return = (final_equity - self.initial_capital) / self.initial_capital
        
        # 最大回撤
        equity_df['peak'] = equity_df['total_equity'].cummax()
        equity_df['drawdown'] = (equity_df['total_equity'] - equity_df['peak']) / equity_df['peak']
        max_drawdown = equity_df['drawdown'].min()
        
        # 勝率
        win_trades = 0
        total_trades = 0
        
        if not trades_df.empty:
            buy_trades = trades_df[trades_df['action'] == 'BUY']
            sell_trades = trades_df[trades_df['action'] == 'SELL']
            
            for i in range(min(len(buy_trades), len(sell_trades))):
                buy_price = buy_trades.iloc[i]['price']
                sell_price = sell_trades.iloc[i]['price']
                if sell_price > buy_price:
                    win_trades += 1
                total_trades += 1
        
        win_rate = win_trades / total_trades if total_trades > 0 else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'total_trades': len(self.trades),
            'win_rate': win_rate,
            'win_rate_pct': win_rate * 100,
            'equity_curve': equity_df,
            'trades': trades_df
        }


# 預設策略範例

def sma_crossover_strategy(short_period: int = 5, long_period: int = 20):
    """
    均線交叉策略
    
    Args:
        short_period: 短均線週期
        long_period: 長均線週期
    
    Returns:
        策略函數
    """
    def strategy(data: pd.DataFrame, idx: int) -> str:
        if idx < long_period:
            return 'HOLD'
        
        # 計算均線
        recent_data = data.iloc[:idx+1]
        ma_short = recent_data['close'].tail(short_period).mean()
        ma_long = recent_data['close'].tail(long_period).mean()
        
        prev_data = data.iloc[:idx]
        ma_short_prev = prev_data['close'].tail(short_period).mean()
        ma_long_prev = prev_data['close'].tail(long_period).mean()
        
        # 黃金交叉 → 買入
        if ma_short > ma_long and ma_short_prev <= ma_long_prev:
            return 'BUY'
        
        # 死亡交叉 → 賣出
        if ma_short < ma_long and ma_short_prev >= ma_long_prev:
            return 'SELL'
        
        return 'HOLD'
    
    return strategy


def rsi_strategy(period: int = 14, oversold: float = 30, overbought: float = 70):
    """
    RSI 策略
    
    Args:
        period: RSI 週期
        oversold: 超賣門檻
        overbought: 超買門檻
    
    Returns:
        策略函數
    """
    def strategy(data: pd.DataFrame, idx: int) -> str:
        if idx < period + 1:
            return 'HOLD'
        
        # 計算 RSI
        recent_data = data.iloc[:idx+1]
        delta = recent_data['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        # RSI < 30 → 買入
        if current_rsi < oversold:
            return 'BUY'
        
        # RSI > 70 → 賣出
        if current_rsi > overbought:
            return 'SELL'
        
        return 'HOLD'
    
    return strategy
