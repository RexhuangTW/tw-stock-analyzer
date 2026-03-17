"""設定檔範例 - 請複製為 settings.py 並修改"""

# 資料來源設定
DATA_SOURCE = "twse"  # twse (上市) / tpex (上櫃)

# 技術指標預設參數
INDICATORS = {
    'ma_periods': [5, 20, 60],
    'rsi_period': 14,
    'macd': {'fast': 12, 'slow': 26, 'signal': 9},
    'kd_period': 9,
}

# 選股篩選預設條件
SCREENER_DEFAULTS = {
    'min_price': 10,
    'min_volume': 1000,  # 張
    'rsi_oversold': 30,
    'rsi_overbought': 70,
}

# 監控設定
MONITOR = {
    'check_interval': 60,  # 秒
    'alert_methods': ['console'],  # console / discord / telegram
}

# Discord 通知設定 (選用)
DISCORD_WEBHOOK_URL = ""

# Telegram 通知設定 (選用)
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""
