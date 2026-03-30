"""雙策略選股模組測試 - SwingStrategy + InvestStrategy"""
import pytest
import pandas as pd
import numpy as np

from src.dual_strategy import SwingStrategy, InvestStrategy, SWING_WEIGHTS, INVEST_WEIGHTS


# ==================== Fixtures ====================

def _make_df(close_series, volume_series=None):
    """從收盤價序列建立含技術指標的 DataFrame"""
    from strategy_backtest import prepare_data

    n = len(close_series)
    dates = pd.date_range('2025-01-01', periods=n)
    if volume_series is None:
        volume_series = [1000] * n

    df = pd.DataFrame({
        'date': dates,
        'open': [c - 0.5 for c in close_series],
        'high': [c + 1 for c in close_series],
        'low': [c - 1 for c in close_series],
        'close': close_series,
        'volume': volume_series,
    })
    return prepare_data(df)


@pytest.fixture
def bullish_df():
    """多頭排列：穩定上漲 30 天"""
    prices = [100 + i * 1.5 for i in range(40)]
    volumes = [1000 + i * 50 for i in range(40)]
    return _make_df(prices, volumes)


@pytest.fixture
def bearish_df():
    """空頭排列：穩定下跌 30 天"""
    prices = [200 - i * 2.0 for i in range(40)]
    return _make_df(prices)


@pytest.fixture
def sideways_df():
    """盤整：價格在區間震盪"""
    base = 100
    prices = [base + 3 * np.sin(i * 0.5) for i in range(40)]
    return _make_df(prices)


@pytest.fixture
def bullish_fin_data():
    """優質基本面資料"""
    return {
        'pe': 12,
        'pb': 1.5,
        'revenue_growth': 0.25,
        'dividend_yield': 0.045,
        'debt_equity': 40,
        'fcf_yield': 0.09,
        'name': '測試公司',
        'sector': 'Technology',
        'dcf': {
            'intrinsic_value': 180.0,
            'safety_margin': 45.0,
        },
    }


@pytest.fixture
def poor_fin_data():
    """差勁基本面資料"""
    return {
        'pe': 55,
        'pb': 4.0,
        'revenue_growth': -0.15,
        'dividend_yield': 0.005,
        'debt_equity': 250,
        'fcf_yield': 0.01,
        'name': '爛公司',
        'sector': 'Industrials',
        'dcf': {
            'intrinsic_value': 50.0,
            'safety_margin': -35.0,
        },
    }


# ==================== SwingStrategy Tests ====================

class TestSwingStrategy:
    """短線操作策略測試"""

    def test_init(self):
        s = SwingStrategy()
        assert s.name == '短線操作'
        assert s.weights == SWING_WEIGHTS

    def test_score_insufficient_data(self):
        """資料不足回傳 None"""
        df = _make_df([100] * 10)
        s = SwingStrategy()
        assert s.score(df) is None

    def test_score_bullish(self, bullish_df):
        """多頭走勢應該拿到較高分"""
        s = SwingStrategy()
        result = s.score(bullish_df)
        assert result is not None
        assert result['score'] > 50
        assert result['ma_trend'] == '多頭'
        assert 'close' in result
        assert 'rsi' in result

    def test_score_bearish(self, bearish_df):
        """空頭走勢應該拿到較低分"""
        s = SwingStrategy()
        result = s.score(bearish_df)
        assert result is not None
        assert result['score'] < 50
        assert result['ma_trend'] == '空頭'

    def test_score_with_fundamentals(self, bullish_df, bullish_fin_data):
        """有基本面資料時分數應更高"""
        s = SwingStrategy()
        score_no_fin = s.score(bullish_df)
        score_with_fin = s.score(bullish_df, fin_data=bullish_fin_data)
        assert score_with_fin['score'] >= score_no_fin['score']

    def test_score_sub_scores_keys(self, bullish_df):
        """sub_scores 應包含所有權重維度"""
        s = SwingStrategy()
        result = s.score(bullish_df)
        for key in SWING_WEIGHTS:
            assert key in result['sub_scores']

    def test_recommendation_strong(self, bullish_df):
        """高分推薦含進場/停損/目標"""
        s = SwingStrategy()
        result = s.score(bullish_df)
        result['stock_id'] = '2330'
        rec = s.make_recommendation(result)

        if rec['score'] >= 50:
            assert 'entry' in rec
            assert 'stop_loss' in rec
            assert 'target' in rec
            assert rec['entry'] < rec['close']
            assert rec['stop_loss'] < rec['entry']
            assert rec['target'] > rec['close']

    def test_recommendation_avoid(self, bearish_df):
        """低分應該建議避開"""
        s = SwingStrategy()
        result = s.score(bearish_df)
        result['stock_id'] = '9999'
        rec = s.make_recommendation(result)

        if rec['score'] < 50:
            assert rec['category'] == '避開'
            assert rec['action'] == '不操作'

    def test_score_normalized_range(self, bullish_df, bearish_df, sideways_df):
        """分數應在 0-100 範圍"""
        s = SwingStrategy()
        for df in [bullish_df, bearish_df, sideways_df]:
            result = s.score(df)
            assert 0 <= result['score'] <= 100


# ==================== InvestStrategy Tests ====================

class TestInvestStrategy:
    """投資佈局策略測試"""

    def test_init(self):
        s = InvestStrategy()
        assert s.name == '投資佈局'
        assert s.weights == INVEST_WEIGHTS

    def test_score_insufficient_data(self):
        """資料不足回傳 None"""
        df = _make_df([100] * 10)
        s = InvestStrategy()
        assert s.score(df) is None

    def test_score_without_fin_data(self, bullish_df):
        """無基本面資料仍可評分"""
        s = InvestStrategy()
        result = s.score(bullish_df)
        assert result is not None
        assert result['intrinsic_value'] is None
        assert result['safety_margin'] is None

    def test_score_with_good_fundamentals(self, sideways_df, bullish_fin_data):
        """好基本面 + DCF 安全邊際大 → 高分"""
        s = InvestStrategy()
        result = s.score(sideways_df, fin_data=bullish_fin_data)
        assert result is not None
        assert result['score'] > 50
        assert result['intrinsic_value'] == 180.0
        assert result['safety_margin'] == 45.0

    def test_score_with_poor_fundamentals(self, sideways_df, poor_fin_data):
        """差基本面 + DCF 高估 → 低分"""
        s = InvestStrategy()
        result = s.score(sideways_df, fin_data=poor_fin_data)
        assert result is not None
        assert result['score'] < 50

    def test_score_sub_scores_keys(self, bullish_df, bullish_fin_data):
        """sub_scores 應包含所有權重維度"""
        s = InvestStrategy()
        result = s.score(bullish_df, fin_data=bullish_fin_data)
        for key in INVEST_WEIGHTS:
            assert key in result['sub_scores']

    def test_recommendation_value(self, sideways_df, bullish_fin_data):
        """價值低估標的應有合理建議"""
        s = InvestStrategy()
        result = s.score(sideways_df, fin_data=bullish_fin_data)
        result['stock_id'] = '1234'
        rec = s.make_recommendation(result)

        if rec['score'] >= 70:
            assert rec['category'] == '價值低估'
            assert rec['action'] == '分批布局'
            assert rec['hold_period'] == '3-6 月'
            assert 'stop_loss' in rec
            assert 'target' in rec

    def test_recommendation_not_suitable(self, bearish_df, poor_fin_data):
        """不適合標的"""
        s = InvestStrategy()
        result = s.score(bearish_df, fin_data=poor_fin_data)
        result['stock_id'] = '9999'
        rec = s.make_recommendation(result)

        if rec['score'] < 55:
            assert rec['category'] == '不適合'

    def test_score_normalized_range(self, bullish_df, bearish_df, sideways_df, bullish_fin_data):
        """分數應在 0-100 範圍"""
        s = InvestStrategy()
        for df in [bullish_df, bearish_df, sideways_df]:
            result = s.score(df, fin_data=bullish_fin_data)
            assert 0 <= result['score'] <= 100


# ==================== Report Generation Tests ====================

class TestReportGeneration:
    """報告生成測試"""

    def test_dual_report_generates_two_files(self, tmp_path, bullish_df):
        """雙策略應產生 swing + invest 兩份報告"""
        from report_generator import generate_swing_report, generate_invest_report

        swing = SwingStrategy()
        invest = InvestStrategy()

        # 模擬結果
        swing_result = swing.score(bullish_df)
        swing_result['stock_id'] = '2330'
        swing_rec = swing.make_recommendation(swing_result)
        swing_rec['stock_id'] = '2330'

        invest_result = invest.score(bullish_df, fin_data={
            'pe': 12, 'pb': 1.5, 'revenue_growth': 0.2,
            'dividend_yield': 0.04, 'debt_equity': 40, 'fcf_yield': 0.08,
            'dcf': {'intrinsic_value': 180, 'safety_margin': 40},
        })
        invest_result['stock_id'] = '2330'
        invest_rec = invest.make_recommendation(invest_result)
        invest_rec['stock_id'] = '2330'

        swing_data = {'buys': [swing_rec], 'watches': [], 'total_analyzed': 1}
        invest_data = {'buys': [invest_rec], 'watches': [], 'total_analyzed': 1}

        names = {'2330': '台積電'}

        swing_text = generate_swing_report(swing_data, '2026-03-26', names)
        invest_text = generate_invest_report(invest_data, '2026-03-26', names)

        assert '短線操作候選' in swing_text
        assert '投資佈局候選' in invest_text
        assert '2330' in swing_text
        assert '2330' in invest_text
        assert '台積電' in swing_text

    def test_swing_report_empty_buys(self):
        """無候選時報告仍可生成"""
        from report_generator import generate_swing_report
        text = generate_swing_report(
            {'buys': [], 'watches': [], 'total_analyzed': 100},
            '2026-03-26', {},
        )
        assert '無強勢候選' in text

    def test_invest_report_empty_buys(self):
        """無候選時報告仍可生成"""
        from report_generator import generate_invest_report
        text = generate_invest_report(
            {'buys': [], 'watches': [], 'total_analyzed': 100},
            '2026-03-26', {},
        )
        assert '無價值低估標的' in text
