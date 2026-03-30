#!/usr/bin/env python3
"""除錯：查看持倉原始資料"""

import shioaji as sj
from dotenv import load_dotenv
import os

load_dotenv()

api = sj.Shioaji(simulation=False)
api.login(
    api_key=os.getenv('SINOPAC_API_KEY'),
    secret_key=os.getenv('SINOPAC_SECRET_KEY')
)

print("查詢持倉原始資料:")
print("=" * 60)

positions = api.list_positions(api.stock_account)

for i, pos in enumerate(positions, 1):
    print(f"\n持倉 {i}:")
    print(f"  code: {pos.code}")
    print(f"  quantity: {pos.quantity}")
    print(f"  yd_quantity: {pos.yd_quantity}")
    print(f"  price: {pos.price}")
    print(f"  last_price: {pos.last_price}")
    print(f"  pnl: {pos.pnl}")
    print(f"  direction: {pos.direction}")
    print()
    print(f"  所有屬性:")
    for attr in dir(pos):
        if not attr.startswith('_'):
            try:
                value = getattr(pos, attr)
                if not callable(value):
                    print(f"    {attr}: {value}")
            except:
                pass

api.logout()
