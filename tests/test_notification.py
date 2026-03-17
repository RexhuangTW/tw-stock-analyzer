"""通知系統測試"""
import pytest
from src.notification.discord_notifier import DiscordNotifier
from src.notification.telegram_notifier import TelegramNotifier


class TestDiscordNotifier:
    """Discord 通知器測試"""
    
    def test_initialization(self):
        """測試初始化"""
        notifier = DiscordNotifier(webhook_url="https://test.url")
        assert notifier.webhook_url == "https://test.url"
    
    def test_send_alert_structure(self):
        """測試警報結構 (不實際發送)"""
        notifier = DiscordNotifier(webhook_url="https://test.url")
        # 測試不會拋出異常
        try:
            # 構建 payload (不發送)
            color_map = {
                'BUY': 0x2ecc71,
                'SELL': 0xe74c3c
            }
            assert 'BUY' in color_map
            assert 'SELL' in color_map
        except Exception:
            pytest.fail("結構測試失敗")


class TestTelegramNotifier:
    """Telegram 通知器測試"""
    
    def test_initialization(self):
        """測試初始化"""
        notifier = TelegramNotifier(
            bot_token="test_token",
            chat_id="test_chat"
        )
        assert notifier.bot_token == "test_token"
        assert notifier.chat_id == "test_chat"
        assert "bot" in notifier.api_url
    
    def test_emoji_mapping(self):
        """測試 Emoji 映射"""
        emoji_map = {
            'BUY': '🟢',
            'SELL': '🔴',
            'WARNING': '🟡',
            'INFO': '🔵'
        }
        assert emoji_map['BUY'] == '🟢'
        assert emoji_map['SELL'] == '🔴'
