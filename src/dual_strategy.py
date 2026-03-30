#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""雙策略選股模組 - 短線操作 + 投資佈局"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from abc import ABC, abstractmethod


# ==================== 評分權重 ====================

SWING_WEIGHTS = {
    'trend': 0.35,        # 趨勢（MA 排列）
    'momentum': 0.25,     # 動能（RSI/MACD/KD）
    'volume': 0.15,       # 成交量
    'breakout': 0.15,     # 突破訊號
    'fundamental': 0.10,  # 基本面加分
}

INVEST_WEIGHTS = {
    'dcf_margin': 0.40,      # DCF 安全邊際
    'profitability': 0.15,   # 獲利能力（ROE/EPS成長）
    'safety': 0.15,          # 財務安全（負債比）
    'trend': 0.20,           # 技術面確認底部
    'valuation': 0.10,       # 其他估值指標
}


class BaseStrategy(ABC):
    """策略基底類別"""

    def __init__(self, name, description, weights):
        self.name = name
        self.description = description
        self.weights = dict(weights)

    @abstractmethod
    def score(self, df, fin_data=None):
        """對股票評分，回傳 dict 或 None"""

    @abstractmethod
    def make_recommendation(self, score_result):
        """根據評分結果產生操作建議"""


class SwingStrategy(BaseStrategy):
    """短線操作策略 - 技術面為主"""

    def __init__(self):
        super().__init__(
            name='短線操作',
            description='1-2 週波段，技術面 70% + 基本面 30%',
            weights=SWING_WEIGHTS,
        )

    def score(self, df, fin_data=None):
        if len(df) < 20:
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        scores = {}

        # --- trend (0.35): MA 排列 ---
        if latest['close'] > latest['ma5'] > latest['ma20']:
            scores['trend'] = 3
        elif latest['close'] > latest['ma20']:
            scores['trend'] = 1
        elif latest['close'] < latest['ma5'] < latest['ma20']:
            scores['trend'] = -2
        else:
            scores['trend'] = 0

        # --- momentum (0.25): RSI + MACD ---
        momentum = 0
        # RSI 50-70 是短線強勢區
        if 50 <= latest['rsi'] <= 70:
            momentum += 2
        elif 40 <= latest['rsi'] < 50:
            momentum += 1
        elif latest['rsi'] > 75:  # 修正：75 以上警示，80 以上嚴重扣分
            momentum -= 3
        elif latest['rsi'] > 70:
            momentum -= 1
        elif latest['rsi'] < 30:
            momentum -= 1

        # MACD 黃金交叉
        if latest['macd_hist'] > 0 and latest['macd_hist'] > prev['macd_hist']:
            momentum += 2
        elif latest['macd_hist'] > 0:
            momentum += 1
        elif latest['macd_hist'] < 0:
            momentum -= 1

        scores['momentum'] = min(max(momentum, -3), 3)

        # --- volume (0.15): 成交量變化 + K線型態 ---
        volume_score = 0
        if 'volume' in df.columns and len(df) >= 5:
            avg_vol = df['volume'].iloc[-6:-1].mean()
            cur_vol = latest.get('volume', 0)
            if avg_vol > 0 and cur_vol > 0:
                vol_ratio = cur_vol / avg_vol
                
                # 判斷當天漲跌
                price_change = (latest['close'] - prev['close']) / prev['close']
                
                # K線位置（收盤在當天區間的位置）
                day_range = latest['high'] - latest['low']
                close_position = 0.5  # 預設中間
                if day_range > 0:
                    close_position = (latest['close'] - latest['low']) / day_range
                
                # 爆量上漲 + 收高點 = 加分
                if vol_ratio > 2.0 and price_change > 0.02 and close_position > 0.7:
                    volume_score = 3  # 強勢買盤
                # 爆量下跌 or 收低點 = 扣分
                elif vol_ratio > 2.0 and (price_change < -0.01 or close_position < 0.3):
                    volume_score = -3  # 出貨訊號
                # 放量上漲
                elif vol_ratio > 1.5 and price_change > 0.01:
                    volume_score = 2
                # 溫和放量
                elif vol_ratio > 1.0:
                    volume_score = 1
                # 縮量
                elif vol_ratio < 0.7:
                    volume_score = -1
                else:
                    volume_score = 0
            else:
                volume_score = 0
        else:
            volume_score = 0
        
        scores['volume'] = volume_score

        # --- breakout (0.15): 突破訊號 + K線型態 ---
        breakout = 0
        
        # K線上下影線分析
        day_range = latest['high'] - latest['low']
        if day_range > 0:
            # 上影線比例
            upper_shadow = (latest['high'] - max(latest['open'], latest['close'])) / day_range
            # 下影線比例
            lower_shadow = (min(latest['open'], latest['close']) - latest['low']) / day_range
            
            # 長上影線（試高失敗）= 扣分
            if upper_shadow > 0.4:
                breakout -= 2
            # 長下影線（有支撐）= 加分
            elif lower_shadow > 0.4:
                breakout += 1
        
        # 突破布林上軌（但要看是否收在上軌之上）
        if latest['close'] > latest['bb_upper']:
            breakout += 2
        elif latest['high'] > latest['bb_upper'] and latest['close'] < latest['bb_upper']:
            breakout -= 1  # 試高失敗
        
        # 突破 20 日高點
        if len(df) >= 20:
            high_20 = df['close'].iloc[-21:-1].max()
            if latest['close'] > high_20:
                breakout += 2
        
        # 跌破布林下軌
        if latest['close'] < latest['bb_lower']:
            breakout -= 2
        
        scores['breakout'] = min(max(breakout, -3), 3)

        # --- fundamental (0.10): 基本面加分 ---
        fund_score = 0
        if fin_data:
            pe = fin_data.get('pe', 0)
            if 0 < pe < 15:
                fund_score += 2
            elif 0 < pe < 25:
                fund_score += 1
            elif pe > 50:
                fund_score -= 1

            rg = fin_data.get('revenue_growth', 0)
            if rg > 0.20:
                fund_score += 2
            elif rg > 0.10:
                fund_score += 1
        scores['fundamental'] = min(max(fund_score, -3), 3)

        # --- 加權合計 ---
        raw = sum(scores[k] * self.weights[k] for k in self.weights)
        max_possible = 3 * sum(self.weights.values())
        min_possible = -3 * sum(self.weights.values())
        normalized = (raw - min_possible) / (max_possible - min_possible) * 100

        change_pct = (latest['close'] - prev['close']) / prev['close'] * 100
        ma_trend = (
            '多頭' if latest['close'] > latest['ma5'] > latest['ma20']
            else '空頭' if latest['close'] < latest['ma5'] < latest['ma20']
            else '盤整'
        )

        return {
            'close': float(latest['close']),
            'change_pct': round(change_pct, 2),
            'rsi': round(float(latest['rsi']), 1),
            'macd_hist': round(float(latest['macd_hist']), 2),
            'ma_trend': ma_trend,
            'score': round(normalized, 1),
            'sub_scores': {k: round(v, 2) for k, v in scores.items()},
        }

    def make_recommendation(self, result):
        price = result['close']
        score = result['score']

        if score >= 70:
            category = '強勢突破'
            stop_loss_pct = 0.05
            target_pct = 0.15
        elif score >= 60:
            category = '趨勢偏多'
            stop_loss_pct = 0.06
            target_pct = 0.12
        elif score >= 50:
            category = '觀察'
            stop_loss_pct = 0.08
            target_pct = 0.10
        else:
            return {**result, 'category': '避開', 'action': '不操作'}

        entry = round(price * 0.98, 1)   # 回檔 2% 買
        stop_loss = round(entry * (1 - stop_loss_pct), 1)  # 從進場價算停損
        target = round(entry * (1 + target_pct), 1)  # 從進場價算目標

        return {
            **result,
            'category': category,
            'entry': entry,
            'stop_loss': stop_loss,
            'stop_loss_pct': f"-{stop_loss_pct*100:.0f}%",
            'target': target,
            'target_pct': f"+{target_pct*100:.0f}%",
            'hold_period': '1-2 週',
        }


class InvestStrategy(BaseStrategy):
    """投資佈局策略 - 基本面為主"""

    def __init__(self):
        super().__init__(
            name='投資佈局',
            description='1-6 月價值投資，基本面 70% + 技術面 30%',
            weights=INVEST_WEIGHTS,
        )

    def score(self, df, fin_data=None):
        if len(df) < 20:
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        scores = {}

        # --- dcf_margin (0.40): DCF 安全邊際 ---
        dcf_score = 0
        intrinsic_value = fin_data.get('dcf_value') if fin_data else None
        safety_margin = fin_data.get('dcf_margin') if fin_data else None
        
        if safety_margin is not None:
                if safety_margin > 50:
                    dcf_score = 3
                elif safety_margin > 30:
                    dcf_score = 2
                elif safety_margin > 15:
                    dcf_score = 1
                elif safety_margin < -20:
                    dcf_score = -2
                elif safety_margin < 0:
                    dcf_score = -1
        scores['dcf_margin'] = dcf_score

        # --- profitability (0.15): ROE / EPS 成長 ---
        profit_score = 0
        if fin_data:
            rg = fin_data.get('revenue_growth', 0)
            if rg > 0.20:
                profit_score += 2
            elif rg > 0.10:
                profit_score += 1
            elif rg < -0.10:
                profit_score -= 1

            dy = fin_data.get('dividend_yield', 0)
            if dy > 0.05:
                profit_score += 2
            elif dy > 0.03:
                profit_score += 1
        scores['profitability'] = min(max(profit_score, -3), 3)

        # --- safety (0.15): 負債比 ---
        safety_score = 0
        if fin_data:
            de = fin_data.get('debt_equity', 0)
            if 0 < de < 50:
                safety_score = 3
            elif de < 100:
                safety_score = 1
            elif de > 200:
                safety_score = -2

            fcf_yield = fin_data.get('fcf_yield', 0)
            if fcf_yield > 0.08:
                safety_score += 1
            elif fcf_yield > 0.05:
                safety_score += 0.5
        scores['safety'] = min(max(safety_score, -3), 3)

        # --- trend (0.20): 技術面確認底部，不在持續下跌 ---
        trend_score = 0
        # 不在持續下跌（RSI > 30）
        if latest['rsi'] > 50:
            trend_score += 2
        elif latest['rsi'] > 30:
            trend_score += 1
        elif latest['rsi'] < 20:
            trend_score -= 2

        # 均線開始翻多
        if latest['ma5'] > latest['ma20']:
            trend_score += 1
        elif latest['close'] < latest['ma5'] < latest['ma20']:
            trend_score -= 1
        scores['trend'] = min(max(trend_score, -3), 3)

        # --- valuation (0.10): PE / PB ---
        val_score = 0
        if fin_data:
            pe = fin_data.get('pe', 0)
            try:
                pe = float(pe) if pe else 0
            except (ValueError, TypeError):
                pe = 0
            if 0 < pe < 10:
                val_score += 3
            elif 0 < pe < 15:
                val_score += 2
            elif 0 < pe < 20:
                val_score += 1
            elif pe > 40:
                val_score -= 1

            pb = fin_data.get('pb', 0)
            try:
                pb = float(pb) if pb else 0
            except (ValueError, TypeError):
                pb = 0
            if 0 < pb < 1:
                val_score += 1
        scores['valuation'] = min(max(val_score, -3), 3)

        # --- 加權合計 ---
        raw = sum(scores[k] * self.weights[k] for k in self.weights)
        max_possible = 3 * sum(self.weights.values())
        min_possible = -3 * sum(self.weights.values())
        normalized = (raw - min_possible) / (max_possible - min_possible) * 100

        change_pct = (latest['close'] - prev['close']) / prev['close'] * 100
        ma_trend = (
            '多頭' if latest['close'] > latest['ma5'] > latest['ma20']
            else '空頭' if latest['close'] < latest['ma5'] < latest['ma20']
            else '盤整'
        )

        return {
            'close': float(latest['close']),
            'change_pct': round(change_pct, 2),
            'rsi': round(float(latest['rsi']), 1),
            'macd_hist': round(float(latest['macd_hist']), 2),
            'ma_trend': ma_trend,
            'score': round(normalized, 1),
            'sub_scores': {k: round(v, 2) for k, v in scores.items()},
            'intrinsic_value': intrinsic_value,
            'safety_margin': safety_margin,
        }

    def make_recommendation(self, result):
        price = result['close']
        score = result['score']
        iv = result.get('intrinsic_value')
        sm = result.get('safety_margin')

        if score >= 70:
            category = '價值低估'
            stop_loss_pct = 0.15
        elif score >= 55:
            category = '觀察佈局'
            stop_loss_pct = 0.20
        else:
            return {**result, 'category': '不適合', 'action': '不操作'}

        stop_loss = round(price * (1 - stop_loss_pct), 1)
        target = round(iv, 1) if iv and iv > price else round(price * 1.30, 1)
        expected_return = round((target / price - 1) * 100, 1)

        return {
            **result,
            'category': category,
            'entry': round(price, 1),
            'stop_loss': stop_loss,
            'stop_loss_pct': f"-{stop_loss_pct*100:.0f}%",
            'target': target,
            'expected_return': f"+{expected_return}%",
            'hold_period': '3-6 月',
            'action': '分批布局' if score >= 70 else '等待回檔',
        }
