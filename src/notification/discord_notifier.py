"""Discord 通知"""
import requests
from typing import Optional
from datetime import datetime


class DiscordNotifier:
    """Discord Webhook 通知器"""
    
    def __init__(self, webhook_url: str):
        """
        Args:
            webhook_url: Discord Webhook URL
        """
        self.webhook_url = webhook_url
    
    def send(self, message: str, title: Optional[str] = None, color: Optional[int] = None) -> bool:
        """
        發送通知
        
        Args:
            message: 訊息內容
            title: 標題 (可選)
            color: 顏色 (Discord 顏色碼,可選)
        
        Returns:
            是否成功
        """
        if title:
            # 使用 Embed 格式
            embed = {
                "title": title,
                "description": message,
                "color": color or 0x3498db,  # 預設藍色
                "timestamp": datetime.utcnow().isoformat()
            }
            payload = {"embeds": [embed]}
        else:
            # 純文字
            payload = {"content": message}
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Discord 通知失敗: {e}")
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
        # 根據類型選擇顏色
        color_map = {
            'BUY': 0x2ecc71,   # 綠色
            'SELL': 0xe74c3c,  # 紅色
            'WARNING': 0xf39c12,  # 橙色
            'INFO': 0x3498db   # 藍色
        }
        
        title = f"🚨 {stock_id} - {alert_type}"
        color = color_map.get(alert_type, 0x95a5a6)
        
        return self.send(details, title=title, color=color)
