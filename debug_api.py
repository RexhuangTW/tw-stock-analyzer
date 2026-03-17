"""Debug API 回傳格式"""
import requests
import json

url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
params = {
    'response': 'json',
    'date': '20260317',
    'stockNo': '2330'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

resp = requests.get(url, params=params, headers=headers)
data = resp.json()

print("📋 API 回傳結構:")
print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])  # 前 2000 字元

if 'fields' in data:
    print("\n欄位名稱:", data['fields'])

if 'data' in data and len(data['data']) > 0:
    print(f"\n第一筆資料 (共 {len(data['data'][0])} 個欄位):")
    for i, val in enumerate(data['data'][0]):
        print(f"  [{i}] {val}")
