#!/usr/bin/env python3
import shioaji as sj
from sinopac_config import SINOPAC_CONFIG

api = sj.Shioaji(simulation=False)
api.login(
    api_key=SINOPAC_CONFIG['api_key'],
    secret_key=SINOPAC_CONFIG['secret_key']
)

print("list_position_detail:")
try:
    details = api.list_position_detail(api.stock_account)
    for d in details:
        print(f"\n{d.code}:")
        print(f"  {d}")
except Exception as e:
    print(f"失敗: {e}")

api.logout()
