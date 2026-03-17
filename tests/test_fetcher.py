"""資料擷取器測試 (含 Mock)"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.data.fetcher import TWSEFetcher


@pytest.fixture
def mock_twse_response():
    """模擬 TWSE API 回應"""
    return {
        'stat': 'OK',
        'date': '20260317',
        'title': '115年03月 2330 台積電',
        'fields': ['日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數', '註記'],
        'data': [
            ['115/03/17', '50,000,000', '100,000,000,000', '2000.00', '2050.00', '1980.00', '2020.00', '+20.00', '300000', ''],
            ['115/03/16', '48,000,000', '96,000,000,000', '1990.00', '2010.00', '1970.00', '2000.00', '+10.00', '280000', ''],
        ]
    }


class TestTWSEFetcher:
    """TWSE 擷取器測試"""
    
    def test_initialization(self):
        """測試初始化"""
        fetcher = TWSEFetcher()
        assert fetcher.session is not None
        assert 'User-Agent' in fetcher.session.headers
    
    @patch('requests.Session.get')
    def test_get_daily_price_success(self, mock_get, mock_twse_response):
        """測試成功取得資料"""
        mock_get.return_value.json.return_value = mock_twse_response
        mock_get.return_value.raise_for_status = Mock()
        
        fetcher = TWSEFetcher()
        df = fetcher.get_daily_price('2330', '20260317')
        
        assert len(df) == 2
        assert 'date' in df.columns
        assert 'close' in df.columns
        assert df.iloc[0]['close'] == 2020.0
    
    @patch('requests.Session.get')
    def test_get_daily_price_api_error(self, mock_get):
        """測試 API 錯誤處理"""
        mock_get.return_value.json.return_value = {'stat': 'ERROR'}
        
        fetcher = TWSEFetcher()
        
        with pytest.raises(ValueError, match='API 回應異常'):
            fetcher.get_daily_price('2330')
    
    @patch('requests.Session.get')
    def test_get_daily_price_connection_error(self, mock_get):
        """測試連線錯誤"""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        fetcher = TWSEFetcher()
        
        with pytest.raises(ConnectionError):
            fetcher.get_daily_price('2330')
    
    def test_date_conversion(self, mock_twse_response):
        """測試民國年轉換"""
        with patch('requests.Session.get') as mock_get:
            mock_get.return_value.json.return_value = mock_twse_response
            mock_get.return_value.raise_for_status = Mock()
            
            fetcher = TWSEFetcher()
            df = fetcher.get_daily_price('2330')
            
            # 115/03/17 → 2026-03-17
            assert df.iloc[0]['date'].year == 2026
            assert df.iloc[0]['date'].month == 3
            assert df.iloc[0]['date'].day == 17
    
    def test_volume_conversion(self, mock_twse_response):
        """測試成交量轉換 (股→張)"""
        with patch('requests.Session.get') as mock_get:
            mock_get.return_value.json.return_value = mock_twse_response
            mock_get.return_value.raise_for_status = Mock()
            
            fetcher = TWSEFetcher()
            df = fetcher.get_daily_price('2330')
            
            # 50,000,000 股 = 50,000 張
            assert df.iloc[0]['volume'] == 50000
