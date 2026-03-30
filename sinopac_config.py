#!/usr/bin/env python3
"""
永豐金 Shioaji API 設定
用於即時看盤和監控，不包含下單功能
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

# API 設定
SINOPAC_CONFIG = {
    'api_key': os.getenv('SINOPAC_API_KEY', ''),  # 永豐 API Key
    'secret_key': os.getenv('SINOPAC_SECRET_KEY', ''),  # 永豐 Secret Key
    'person_id': os.getenv('SINOPAC_PERSON_ID', ''),  # 身分證字號
    'ca_cert_path': os.getenv('SINOPAC_CA_CERT_PATH', ''),  # CA 憑證路徑
    'ca_password': os.getenv('SINOPAC_CA_PASSWORD', ''),  # 憑證密碼
}

def check_config():
    """檢查設定是否完整"""
    missing = []
    for key, value in SINOPAC_CONFIG.items():
        if not value:
            missing.append(key)
    
    if missing:
        print("⚠️ 永豐 API 設定不完整，缺少以下項目：")
        for key in missing:
            print(f"  - {key}")
        print()
        print("請設定環境變數或修改 sinopac_config.py")
        return False
    
    print("✅ 永豐 API 設定完整")
    return True

if __name__ == '__main__':
    check_config()
