#!/usr/bin/env python3
"""
永豐 API 測試報告
完成此測試以啟用正式環境
"""

import shioaji as sj
from datetime import datetime
from sinopac_config import SINOPAC_CONFIG, check_config

def test_login():
    """測試 1: 登入測試"""
    print("=" * 60)
    print("測試 1: 登入測試")
    print("=" * 60)
    
    if not check_config():
        return False
    
    try:
        # 使用模擬模式
        api = sj.Shioaji(simulation=True)
        
        print(f"Shioaji 版本: {sj.__version__}")
        print("嘗試登入模擬環境...")
        
        accounts = api.login(
            api_key=SINOPAC_CONFIG['api_key'],
            secret_key=SINOPAC_CONFIG['secret_key']
        )
        
        print("✅ 登入成功")
        print(f"帳戶: {accounts}")
        
        return api, accounts
        
    except Exception as e:
        print(f"❌ 登入失敗: {e}")
        return None, None

def test_stock_order(api):
    """測試 2: 證券下單測試"""
    print()
    print("=" * 60)
    print("測試 2: 證券下單測試")
    print("=" * 60)
    
    try:
        # 使用元大金 (2890) 做測試
        contract = api.Contracts.Stocks.TSE["2890"]
        print(f"商品: {contract.code} {contract.name}")
        
        # 證券委託單
        order = api.Order(
            price=18,  # 價格
            quantity=1,  # 1張
            action=sj.constant.Action.Buy,  # 買進
            price_type=sj.constant.StockPriceType.LMT,  # 限價
            order_type=sj.constant.OrderType.ROD,  # 當日有效
            account=api.stock_account  # 證券帳號
        )
        
        print("送出測試委託...")
        trade = api.place_order(contract, order)
        
        print()
        print("委託結果:")
        print(f"  委託ID: {trade.status.id}")
        print(f"  狀態: {trade.status.status}")
        print(f"  狀態碼: {trade.status.status_code}")
        print(f"  時間: {trade.status.order_datetime}")
        
        if trade.status.status_code == '00':
            print("✅ 證券下單測試成功")
            return True
        else:
            print(f"⚠️ 委託狀態異常: {trade.status.status}")
            return False
            
    except Exception as e:
        print(f"❌ 證券下單測試失敗: {e}")
        return False

def activate_certificate(api):
    """啟用憑證"""
    print()
    print("=" * 60)
    print("啟用憑證")
    print("=" * 60)
    
    try:
        result = api.activate_ca(
            ca_path=SINOPAC_CONFIG['ca_cert_path'],
            ca_passwd=SINOPAC_CONFIG['ca_password'],
            person_id=SINOPAC_CONFIG['person_id'],
        )
        
        if result:
            print("✅ 憑證啟用成功")
        else:
            print("❌ 憑證啟用失敗")
        
        return result
        
    except Exception as e:
        print(f"⚠️ 憑證啟用錯誤: {e}")
        print("（模擬環境可能不需要啟用憑證）")
        return None

def check_test_status():
    """檢查測試狀態（正式環境）"""
    print()
    print("=" * 60)
    print("檢查測試狀態（正式環境）")
    print("=" * 60)
    
    try:
        # 使用正式環境
        api = sj.Shioaji(simulation=False)
        
        print("登入正式環境...")
        accounts = api.login(
            api_key=SINOPAC_CONFIG['api_key'],
            secret_key=SINOPAC_CONFIG['secret_key']
        )
        
        print()
        print("帳戶狀態:")
        for acc in accounts:
            print(f"\n{type(acc).__name__}:")
            print(f"  帳號: {acc.account_id}")
            print(f"  簽署狀態: {getattr(acc, 'signed', 'N/A')}")
            
            if hasattr(acc, 'signed'):
                if acc.signed:
                    print("  ✅ 已通過 API 測試")
                else:
                    print("  ❌ 尚未通過 API 測試")
        
        api.logout()
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

def main():
    """主程式"""
    print("永豐 API 測試報告")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 測試 1: 登入
    api, accounts = test_login()
    if not api:
        return
    
    # 測試 2: 證券下單
    import time
    time.sleep(2)  # 間隔 2 秒
    stock_ok = test_stock_order(api)
    
    # 啟用憑證
    time.sleep(2)
    activate_certificate(api)
    
    # 登出
    api.logout()
    
    print()
    print("=" * 60)
    print("測試總結")
    print("=" * 60)
    print(f"登入測試: ✅")
    print(f"證券下單: {'✅' if stock_ok else '❌'}")
    print()
    print("完成模擬測試後，請等待 5 分鐘讓系統審核。")
    print("然後執行以下指令檢查測試狀態:")
    print("  python3 sinopac_test.py --check")
    
    # 如果有參數 --check，檢查測試狀態
    import sys
    if '--check' in sys.argv:
        time.sleep(2)
        check_test_status()

if __name__ == '__main__':
    main()
