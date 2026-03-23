#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DCF 基本面分析模組 - 對觀察名單進行內在價值估算"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import json
import time
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime

import yfinance as yf
import pandas as pd
import numpy as np

DCF_RESULT_FILE = Path(__file__).parent / "dcf_results.json"

# 產業平均成長率 (備用)
INDUSTRY_GROWTH = {
    'Technology': 0.15,
    'Semiconductors': 0.20,
    'Financial Services': 0.08,
    'Consumer Cyclical': 0.10,
    'Industrials': 0.08,
    'Healthcare': 0.12,
    'Communication Services': 0.10,
    'Consumer Defensive': 0.06,
    'Energy': 0.05,
    'Utilities': 0.04,
    'Real Estate': 0.06,
    'Basic Materials': 0.07,
    'default': 0.08,
}

def get_financial_data(stock_id):
    """取得股票的財務數據"""
    # 上市用 .TW，上櫃用 .TWO
    for suffix in ['.TW', '.TWO']:
        try:
            symbol = f"{stock_id}{suffix}"
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or info.get('regularMarketPrice') is None:
                continue
            
            # 基本資訊
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            if price == 0:
                continue
            
            # 財務數據
            market_cap = info.get('marketCap', 0)
            shares = info.get('sharesOutstanding', 0)
            
            # 獲利能力
            revenue = info.get('totalRevenue', 0)
            net_income = info.get('netIncomeToCommon', 0)
            fcf = info.get('freeCashflow', 0)
            operating_cf = info.get('operatingCashflow', 0)
            
            # 成長性
            revenue_growth = info.get('revenueGrowth', 0) or 0
            earnings_growth = info.get('earningsGrowth', 0) or 0
            
            # 估值
            pe = info.get('trailingPE', 0) or 0
            forward_pe = info.get('forwardPE', 0) or 0
            pb = info.get('priceToBook', 0) or 0
            
            # 股利
            dividend_yield = info.get('dividendYield', 0) or 0
            
            # 風險
            beta = info.get('beta', 1.0) or 1.0
            debt_equity = info.get('debtToEquity', 0) or 0
            
            # 產業
            sector = info.get('sector', 'default')
            industry = info.get('industry', '')
            name = info.get('shortName', stock_id)
            
            # 計算 FCF margin
            fcf_margin = fcf / revenue if revenue > 0 else 0
            
            # 計算 FCF yield
            fcf_yield = fcf / market_cap if market_cap > 0 else 0
            
            return {
                'stock_id': stock_id,
                'symbol': symbol,
                'name': name,
                'sector': sector,
                'industry': industry,
                'price': price,
                'market_cap': market_cap,
                'shares': shares,
                'revenue': revenue,
                'net_income': net_income,
                'fcf': fcf,
                'operating_cf': operating_cf,
                'revenue_growth': revenue_growth,
                'earnings_growth': earnings_growth,
                'pe': pe,
                'forward_pe': forward_pe,
                'pb': pb,
                'dividend_yield': dividend_yield,
                'beta': beta,
                'debt_equity': debt_equity,
                'fcf_margin': fcf_margin,
                'fcf_yield': fcf_yield,
            }
        except Exception:
            continue
    
    return None


def calculate_dcf(data, projection_years=5, terminal_growth=0.03):
    """計算 DCF 內在價值"""
    
    if not data or data['fcf'] <= 0 or data['shares'] <= 0:
        return None
    
    # WACC 計算
    risk_free_rate = 0.015  # 台灣無風險利率 ~1.5%
    market_premium = 0.065  # 市場風險溢酬
    beta = min(max(data['beta'], 0.5), 2.5)  # 限制 beta 範圍
    
    cost_of_equity = risk_free_rate + beta * market_premium
    
    # 簡化 WACC (假設主要靠股權融資)
    debt_ratio = min(data['debt_equity'] / (100 + data['debt_equity']), 0.5) if data['debt_equity'] > 0 else 0.1
    cost_of_debt = 0.03  # 假設借款利率 3%
    tax_rate = 0.20  # 營所稅率
    
    wacc = cost_of_equity * (1 - debt_ratio) + cost_of_debt * (1 - tax_rate) * debt_ratio
    wacc = max(wacc, 0.06)  # WACC 最低 6%
    
    # 成長率估算
    sector = data.get('sector', 'default')
    industry_growth = INDUSTRY_GROWTH.get(sector, INDUSTRY_GROWTH['default'])
    
    # 混合成長率: 公司歷史成長 + 產業平均
    company_growth = data['revenue_growth']
    if company_growth > 0:
        growth_rate = company_growth * 0.6 + industry_growth * 0.4
    else:
        growth_rate = industry_growth
    
    # 限制成長率在合理範圍
    growth_rate = min(max(growth_rate, 0.02), 0.35)
    
    # 成長率遞減 (前幾年高，後幾年低)
    growth_rates = []
    for i in range(projection_years):
        decay = growth_rate * (1 - i * 0.15)  # 每年衰減 15%
        growth_rates.append(max(decay, terminal_growth + 0.02))
    
    # FCF 預測
    current_fcf = data['fcf']
    projected_fcfs = []
    fcf = current_fcf
    
    for g in growth_rates:
        fcf = fcf * (1 + g)
        projected_fcfs.append(fcf)
    
    # 折現 FCF
    pv_fcfs = []
    for i, cf in enumerate(projected_fcfs):
        pv = cf / (1 + wacc) ** (i + 1)
        pv_fcfs.append(pv)
    
    pv_fcf_total = sum(pv_fcfs)
    
    # 終端價值
    terminal_fcf = projected_fcfs[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth)
    pv_terminal = terminal_value / (1 + wacc) ** projection_years
    
    # 企業價值
    enterprise_value = pv_fcf_total + pv_terminal
    
    # 股權價值 (簡化: 不扣淨負債)
    equity_value = enterprise_value
    
    # 每股內在價值
    intrinsic_value = equity_value / data['shares']
    
    # 轉換為台幣 (Yahoo 回傳的可能是台幣或美元)
    if intrinsic_value < 10 and data['price'] > 100:
        # 可能是美元，轉換
        intrinsic_value *= 32.5
    
    # 安全邊際
    safety_margin = (intrinsic_value - data['price']) / intrinsic_value
    
    return {
        'intrinsic_value': round(intrinsic_value, 1),
        'safety_margin': round(safety_margin * 100, 1),
        'wacc': round(wacc * 100, 1),
        'growth_rate': round(growth_rates[0] * 100, 1),
        'terminal_growth': round(terminal_growth * 100, 1),
        'pv_fcf': round(pv_fcf_total / 1e9, 1),
        'pv_terminal': round(pv_terminal / 1e9, 1),
        'fcf_yield': round(data['fcf_yield'] * 100, 2),
    }


def analyze_watchlist(watchlist):
    """對觀察名單進行 DCF 分析"""
    
    results = []
    
    for stock in watchlist:
        stock_id = stock['stock_id']
        tech_score = stock.get('score', 0)
        
        try:
            # 取得財務數據
            fin_data = get_financial_data(stock_id)
            if not fin_data:
                continue
            
            # DCF 估值
            dcf = calculate_dcf(fin_data)
            
            # 基本面評分
            fundamental_score = 0
            
            # PE 評分
            if fin_data['pe'] > 0:
                if fin_data['pe'] < 10:
                    fundamental_score += 3
                elif fin_data['pe'] < 15:
                    fundamental_score += 2
                elif fin_data['pe'] < 20:
                    fundamental_score += 1
                elif fin_data['pe'] > 40:
                    fundamental_score -= 2
            
            # 殖利率評分
            if fin_data['dividend_yield'] > 0.05:
                fundamental_score += 3
            elif fin_data['dividend_yield'] > 0.03:
                fundamental_score += 2
            elif fin_data['dividend_yield'] > 0.01:
                fundamental_score += 1
            
            # 成長率評分
            if fin_data['revenue_growth'] > 0.20:
                fundamental_score += 3
            elif fin_data['revenue_growth'] > 0.10:
                fundamental_score += 2
            elif fin_data['revenue_growth'] > 0:
                fundamental_score += 1
            
            # DCF 安全邊際評分
            if dcf:
                if dcf['safety_margin'] > 30:
                    fundamental_score += 3
                elif dcf['safety_margin'] > 15:
                    fundamental_score += 2
                elif dcf['safety_margin'] > 0:
                    fundamental_score += 1
                elif dcf['safety_margin'] < -30:
                    fundamental_score -= 2
            
            # FCF yield 評分
            if fin_data['fcf_yield'] > 0.08:
                fundamental_score += 2
            elif fin_data['fcf_yield'] > 0.05:
                fundamental_score += 1
            
            # 綜合評分 (技術面 50% + 基本面 50%)
            max_fundamental = 14
            fundamental_normalized = (fundamental_score / max_fundamental) * 100
            combined_score = tech_score * 0.5 + fundamental_normalized * 0.5
            
            result = {
                'stock_id': stock_id,
                'name': fin_data['name'],
                'sector': fin_data['sector'],
                'price': fin_data['price'],
                'tech_score': tech_score,
                'fundamental_score': round(fundamental_normalized, 1),
                'combined_score': round(combined_score, 1),
                'pe': round(fin_data['pe'], 1),
                'dividend_yield': round(fin_data['dividend_yield'] * 100, 2),
                'revenue_growth': round(fin_data['revenue_growth'] * 100, 1),
                'fcf_yield': round(fin_data['fcf_yield'] * 100, 2),
                'intrinsic_value': dcf['intrinsic_value'] if dcf else None,
                'safety_margin': dcf['safety_margin'] if dcf else None,
                'wacc': dcf['wacc'] if dcf else None,
                'recommendation': '',
            }
            
            # 建議
            if dcf and dcf['safety_margin'] > 15 and tech_score >= 60:
                result['recommendation'] = '買進 (技術+基本面雙確認)'
            elif dcf and dcf['safety_margin'] > 0 and tech_score >= 55:
                result['recommendation'] = '觀察 (基本面低估)'
            elif dcf and dcf['safety_margin'] < -20:
                result['recommendation'] = '避開 (高估)'
            else:
                result['recommendation'] = '中性'
            
            results.append(result)
            time.sleep(0.3)
            
        except Exception as e:
            continue
    
    # 按綜合評分排序
    results.sort(key=lambda x: x['combined_score'], reverse=True)
    
    return results


def run_dcf_analysis():
    """讀取今日選股觀察名單，執行 DCF 分析"""
    
    picks_file = Path(__file__).parent / "today_picks.json"
    if not picks_file.exists():
        print("無選股結果")
        return
    
    with open(picks_file) as f:
        picks = json.load(f)
    
    watchlist = picks.get('watches', []) + picks.get('buys', [])
    
    if not watchlist:
        print("觀察名單為空")
        return
    
    print(f"=== DCF 基本面分析 ===")
    print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"分析標的: {len(watchlist)} 檔")
    print()
    
    results = analyze_watchlist(watchlist)
    
    # 輸出
    print(f"{'股票':6s} {'名稱':10s} {'現價':>8s} {'技術':>5s} {'基本':>5s} {'綜合':>5s} {'內在價值':>8s} {'安全邊際':>7s} {'建議'}")
    print("-" * 85)
    
    for r in results:
        iv = f"{r['intrinsic_value']:.0f}" if r['intrinsic_value'] else "N/A"
        sm = f"{r['safety_margin']:+.1f}%" if r['safety_margin'] is not None else "N/A"
        print(f"{r['stock_id']:6s} {r['name'][:10]:10s} {r['price']:8.1f} {r['tech_score']:5.1f} {r['fundamental_score']:5.1f} {r['combined_score']:5.1f} {iv:>8s} {sm:>7s}  {r['recommendation']}")
    
    # 儲存結果
    output = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'results': results,
    }
    
    with open(DCF_RESULT_FILE, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n結果儲存: {DCF_RESULT_FILE}")
    
    return results


if __name__ == "__main__":
    run_dcf_analysis()
