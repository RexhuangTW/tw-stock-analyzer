# 🔧 UV 環境設定指南

由於 `uv run` 會建立隔離環境，需要先安裝專案本身才能正確找到 `src` 模組。

## 📦 安裝步驟

### 1. 同步依賴並安裝專案
```bash
cd /Users/rex-mbp/tw-stock-analyzer
uv sync
```

這會：
- 建立虛擬環境 (.venv)
- 安裝所有依賴套件
- 將專案本身安裝為可編輯模式

### 2. 啟動應用
```bash
uv run streamlit run app.py
```

---

## 🚀 快速啟動腳本

我們更新了 `run_app.sh` 來自動處理這些步驟。

直接執行：
```bash
./run_app.sh
```

---

## 🔍 驗證安裝

檢查專案是否正確安裝：
```bash
uv run python -c "from src.data.fetcher import TWSEFetcher; print('✅ 模組可用')"
```

---

## ❓ 常見問題

### Q: 為什麼不能直接用 `python3 -m streamlit`？
A: 可以，但需要全域安裝 streamlit。使用 `uv` 可以隔離專案環境，避免套件衝突。

### Q: 修改程式碼後需要重新安裝嗎？
A: 不需要！`uv sync` 使用可編輯模式 (editable install)，程式碼改動會立即生效。

---

**如遇到問題，請先執行:** `uv sync`
