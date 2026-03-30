#!/usr/bin/env python3
"""快速檢查永豐 API 測試狀態"""

import shioaji as sj
import traceback
from sinopac_config import SINOPAC_CONFIG

def check_status():
    try:
        print("初始化 Shioaji...")
        api = sj.Shioaji(simulation=False)
        
        print(f"Shioaji 版本: {sj.__version__}")
        print("嘗試登入正式環境...")
        
        accounts = api.login(
            api_key=SINOPAC_CONFIG['api_key'],
            secret_key=SINOPAC_CONFIG['secret_key']
        )
        
        print("\n✅ 登入成功")
        print("\n帳戶狀態:")
        
        for acc in accounts:
            acc_type = type(acc).__name__
            print(f"\n{acc_type}:")
            print(f"  帳號: {acc.account_id}")
            
            # 檢查簽署狀態（測試狀態）
            if hasattr(acc, 'signed'):
                signed = acc.signed
                print(f"  簽署狀態: {signed}")
                if signed:
                    print("  ✅ 已通過 API 測試，可啟用正式環境")
                else:
                    print("  ❌ 尚未通過 API 測試")
                    print("  📝 請先完成模擬下單測試")
            else:
                print("  ⚠️ 無法取得簽署狀態")
        
        api.logout()
        print("\n已登出")
        
    except Exception as e:
        print(f"\n❌ 執行失敗: {e}")
        print("\n詳細錯誤:")
        traceback.print_exc()

if __name__ == '__main__':
    check_status()
