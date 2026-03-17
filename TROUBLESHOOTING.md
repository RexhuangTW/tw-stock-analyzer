# 🔧 台股分析器 - 問題排查指南

## ❌ 錯誤: No module named 'src.data'

### 原因
Python 無法找到 `src` 模組，通常是因為執行時的工作目錄不正確。

### ✅ 解決方案

#### 方案 1: 使用啟動腳本 (推薦)
```bash
cd /Users/clawagent/.openclaw/workspace/tw-stock-analyzer
./run_app.sh
```

或直接執行:
```bash
bash /Users/clawagent/.openclaw/workspace/tw-stock-analyzer/run_app.sh
```

#### 方案 2: 手動切換目錄
```bash
cd /Users/clawagent/.openclaw/workspace/tw-stock-analyzer
streamlit run app.py
```

⚠️ **重點:** 必須在專案根目錄執行，不能在其他目錄執行！

#### 方案 3: 檢查工作目錄
```bash
# 確認目前在正確目錄
pwd
# 應該顯示: /Users/clawagent/.openclaw/workspace/tw-stock-analyzer

# 檢查 src 目錄存在
ls src/
# 應該顯示: backtest data indicators monitor notification screener visualization
```

---

## ❌ 錯誤: ModuleNotFoundError: No module named 'streamlit'

### 原因
缺少依賴套件

### ✅ 解決方案
```bash
cd /Users/clawagent/.openclaw/workspace/tw-stock-analyzer
pip3 install -r requirements.txt
```

---

## ❌ 錯誤: SSL 警告

### 原因
macOS 系統使用 LibreSSL 而非 OpenSSL

### ✅ 解決方案
這是警告不影響功能，可以忽略。或升級 urllib3:
```bash
pip3 install --upgrade urllib3
```

---

## ❌ 執行 demo 腳本失敗

### 原因
需要在專案根目錄執行

### ✅ 解決方案
```bash
cd /Users/clawagent/.openclaw/workspace/tw-stock-analyzer

# 執行示範
python3 demo.py
python3 demo_backtest.py
python3 demo_interactive.py
python3 demo_advanced_screening.py
```

---

## 🧪 測試環境

### 檢查 Python 版本
```bash
python3 --version
# 需要 Python 3.9+
```

### 檢查依賴安裝
```bash
python3 -c "import streamlit; print(streamlit.__version__)"
python3 -c "import pandas; print(pandas.__version__)"
python3 -c "import plotly; print(plotly.__version__)"
```

### 測試模組導入
```bash
cd /Users/clawagent/.openclaw/workspace/tw-stock-analyzer
python3 -c "from src.data.fetcher import TWSEFetcher; print('✅ 模組正常')"
```

---

## 📊 執行測試

```bash
cd /Users/clawagent/.openclaw/workspace/tw-stock-analyzer
pytest tests/ -v
```

應該顯示: `73 passed`

---

## 🚀 正確啟動方式總結

### Web UI (Streamlit)
```bash
cd /Users/clawagent/.openclaw/workspace/tw-stock-analyzer
streamlit run app.py
```
或
```bash
./run_app.sh
```

### 命令列示範
```bash
cd /Users/clawagent/.openclaw/workspace/tw-stock-analyzer
python3 demo.py
```

### Python API
```python
import sys
sys.path.insert(0, '/Users/clawagent/.openclaw/workspace/tw-stock-analyzer')

from src.data.fetcher import TWSEFetcher
# ... 使用
```

---

## 🆘 仍然無法解決？

### 檢查清單
- [ ] 是否在專案根目錄? (`pwd` 確認)
- [ ] src/ 目錄是否存在? (`ls src/`)
- [ ] 所有 __init__.py 是否存在? (`find src -name "__init__.py"`)
- [ ] 依賴是否安裝? (`pip3 list | grep streamlit`)
- [ ] Python 版本是否 3.9+? (`python3 --version`)

### 重新安裝
```bash
cd /Users/clawagent/.openclaw/workspace/tw-stock-analyzer
pip3 uninstall -y streamlit pandas plotly
pip3 install -r requirements.txt
```

---

**最常見問題:** 在錯誤的目錄執行！  
**解決方法:** 先 `cd` 到專案根目錄再執行。
