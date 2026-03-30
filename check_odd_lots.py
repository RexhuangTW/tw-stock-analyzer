#!/usr/bin/env python3
"""檢查是否有專門查詢零股的方法"""

import shioaji as sj
from dotenv import load_dotenv
import os

load_dotenv()

api = sj.Shioaji(simulation=False)
api.login(
    api_key=os.getenv('SINOPAC_API_KEY'),
    secret_key=os.getenv('SINOPAC_SECRET_KEY')
)

print("查詢帳戶資訊:")
print("=" * 60)
print(f"證券帳號: {api.stock_account}")
print()

# 檢查有什麼方法可以查詢
print("API 可用方法:")
print("=" * 60)
for method in dir(api):
    if 'position' in method.lower() or 'settlement' in method.lower() or 'balance' in method.lower():
        print(f"  {method}")

# 嘗試其他查詢方式
print()
print("嘗試其他查詢方法:")
print("=" * 60)

try:
    # 試試看 settlements
    settlements = api.settlements(api.stock_account)
    print(f"settlements: {settlements}")
except Exception as e:
    print(f"settlements 失敗: {e}")

try:
    # 試試看 account_balance
    balance = api.account_balance()
    print(f"account_balance: {balance}")
except Exception as e:
    print(f"account_balance 失敗: {e}")

api.logout()
