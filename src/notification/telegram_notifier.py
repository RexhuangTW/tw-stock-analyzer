"""Telegram 通知"""
from typing import Optional
import requests


class TelegramNotifier:
    """Telegram Bot 通知器"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Args:
            bot_token: Telegram Bot Token
            chat_id: Chat ID (可從 @userinfobot 取得)
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send(self, message: str, parse_mode: str = "Markdown") -> bool:
        """
        發送通知
        
        Args:
            message: 訊息內容
            parse_mode: 解析模式 ('Markdown' 或 'HTML')
        
        Returns:
            是否成功
        """
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Telegram 通知失敗: {e}")
            return False
    
    def send_alert(self, stock_id: str, alert_type: str, details: str) -> bool:
        """
        發送股票警報
        
        Args:
            stock_id: 股票代號
            alert_type: 警報類型
            details: 詳細資訊
        
        Returns:
            是否成功
        """
        # Emoji 映射
        emoji_map = {
            'BUY': '🟢',
            'SELL': '🔴',
            'WARNING': '🟡',
            'INFO': '🔵'
        }
        
        emoji = emoji_map.get(alert_type, '⚪')
        message = f"{emoji} *{stock_id} - {alert_type}*\n\n{details}"
        
        return self.send(message)
    
    def send_photo(self, photo_path: str, caption: Optional[str] = None) -> bool:
        """
        發送圖片
        
        Args:
            photo_path: 圖片檔案路徑
            caption: 圖片說明 (可選)
        
        Returns:
            是否成功
        """
        url = f"{self.api_url}/sendPhoto"
        
        try:
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': self.chat_id}
                if caption:
                    data['caption'] = caption
                
                response = requests.post(url, files=files, data=data, timeout=30)
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"❌ Telegram 圖片發送失敗: {e}")
            return False
