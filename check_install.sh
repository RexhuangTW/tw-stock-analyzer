#!/bin/bash
cd "$(dirname "$0")"

echo "檢查已安裝的套件..."
uv run python -c "
import sys
import site

print('Python 路徑:')
for p in sys.path[:10]:
    print(f'  {p}')

print('\n已安裝套件位置:')
print(f'  {site.getsitepackages()}')

print('\n檢查 src 是否在已安裝套件中...')
import os
for sp in site.getsitepackages():
    if os.path.exists(sp):
        items = os.listdir(sp)
        src_items = [i for i in items if 'src' in i.lower() or 'tw-stock' in i.lower()]
        if src_items:
            print(f'  在 {sp} 找到:')
            for item in src_items:
                print(f'    - {item}')
"
