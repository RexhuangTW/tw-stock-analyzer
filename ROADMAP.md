# 🗺️ 台股分析器 - 優化與擴充計畫

**版本:** v1.0 → v2.0  
**規劃日期:** 2026-03-17  
**目標:** 提升效能、完善測試、增加實用功能

---

## 📊 現況分析

### ✅ 已完成 (v1.0)
- 6 大核心模組 (資料/指標/選股/監控/回測/視覺化)
- 1,670 行程式碼
- 25 個單元測試 (100% 通過)
- 4 種專業圖表
- 完整文件

### ⚠️ 待改進
- **測試覆蓋率偏低** (28% 整體,核心模組 70-100%)
- **資料擷取速度慢** (~20 秒抓 6 個月)
- **無盤中即時報價** (僅收盤價)
- **圖表非互動式** (靜態 PNG)
- **無資料快取機制** (重複請求浪費時間)

---

## 🎯 優化計畫

### Phase 1: 程式碼品質優化 (1-2 週)

#### 1.1 提升測試覆蓋率 → 目標 80%

**現況:** 28% (核心模組 70-100%)  
**目標:** 80% 整體覆蓋率

**TODO:**
- [ ] 新增資料擷取模組測試 (`test_data.py`)
  - Mock TWSE API 回應
  - 測試民國年轉換
  - 測試資料清理邏輯
  - 測試錯誤處理
- [ ] 新增監控模組測試 (`test_monitor.py`)
  - 測試觸發條件
  - 測試警報處理器
  - 測試持續監控邏輯
- [ ] 新增視覺化模組測試 (`test_visualization.py`)
  - 測試圖表生成 (不儲存檔案)
  - 測試資料格式驗證
  - 測試錯誤處理
- [ ] 新增整合測試 (`test_integration.py`)
  - 完整選股流程測試
  - 完整回測流程測試

**預估工時:** 8-12 小時  
**優先級:** ⭐⭐⭐ HIGH

---

#### 1.2 程式碼重構與優化

**TODO:**
- [ ] **資料擷取加速**
  - 實作快取機制 (SQLite 或檔案快取)
  - 避免重複請求相同資料
  - 批次請求優化
  
  ```python
  # 範例: 簡單檔案快取
  def get_cached_data(stock_id, date):
      cache_file = f"cache/{stock_id}_{date}.pkl"
      if os.path.exists(cache_file):
          return pd.read_pickle(cache_file)
      
      data = fetch_from_api(stock_id, date)
      data.to_pickle(cache_file)
      return data
  ```

- [ ] **型別標註 (Type Hints)**
  - 所有函數加上型別標註
  - 使用 `mypy` 靜態檢查
  
  ```python
  def calculate_ma(prices: pd.Series, period: int) -> pd.Series:
      return prices.rolling(window=period).mean()
  ```

- [ ] **錯誤處理增強**
  - 自訂 Exception 類別
  - 統一錯誤訊息格式
  - 加入 logging 機制

- [ ] **設定檔管理**
  - 將 `settings.example.py` 改為 `config.yaml`
  - 支援環境變數 (`.env`)
  - 使用 `pydantic` 驗證設定

**預估工時:** 12-16 小時  
**優先級:** ⭐⭐⭐ HIGH

---

#### 1.3 效能優化

**TODO:**
- [ ] **指標計算向量化**
  - 使用 NumPy 加速 RSI/MACD 計算
  - 避免迴圈,改用向量運算
  
- [ ] **平行處理**
  - 批次選股使用 `multiprocessing`
  - 多檔股票同時抓取資料
  
  ```python
  from multiprocessing import Pool
  
  def screen_parallel(stock_ids, strategy):
      with Pool(4) as p:
          results = p.map(analyze_stock, stock_ids)
      return pd.concat(results)
  ```

- [ ] **記憶體優化**
  - 大資料集使用 `chunking`
  - 及時釋放不需要的 DataFrame

**預估工時:** 6-8 小時  
**優先級:** ⭐⭐ MEDIUM

---

### Phase 2: 功能擴充 (2-4 週)

#### 2.1 資料源擴充 ✨

**目標:** 支援更多資料來源與即時報價

**TODO:**
- [ ] **櫃買中心 (TPEX) 整合**
  - 上櫃股票資料擷取
  - 統一資料格式
  
- [ ] **Yahoo Finance API**
  - 美股資料支援
  - 即時報價 (延遲 15-20 分鐘)
  
  ```python
  import yfinance as yf
  
  def get_yahoo_data(symbol, period='1y'):
      ticker = yf.Ticker(symbol)
      return ticker.history(period=period)
  ```

- [ ] **證交所盤中報價 (WebSocket)**
  - 真正的即時報價
  - 需要處理連線穩定性
  
- [ ] **基本面資料**
  - 財報資料 (EPS, 營收, 毛利率)
  - 股利資料
  - 法人買賣超

**預估工時:** 16-24 小時  
**優先級:** ⭐⭐⭐ HIGH

---

#### 2.2 進階技術指標 ✨

**TODO:**
- [ ] **Volume Profile (量價分析)**
- [ ] **Ichimoku Cloud (一目均衡表)**
- [ ] **Fibonacci Retracement (費波那契回調)**
- [ ] **ATR (Average True Range,真實波動幅度)**
- [ ] **OBV (On-Balance Volume,能量潮)**
- [ ] **威廉指標 (%R)**
- [ ] **CCI (Commodity Channel Index)**

**預估工時:** 8-12 小時  
**優先級:** ⭐⭐ MEDIUM

---

#### 2.3 進階選股策略 ✨

**TODO:**
- [ ] **量價突破策略**
  - 放量突破前高
  - 縮量整理後突破
  
- [ ] **布林通道突破**
  - 突破上軌 + 量增
  - 跌破下軌反彈
  
- [ ] **多因子選股**
  - 基本面 + 技術面綜合評分
  - 可自訂權重
  
  ```python
  def multi_factor_score(stock_data):
      score = 0
      score += tech_score(stock_data) * 0.6  # 技術面 60%
      score += fundamental_score(stock_data) * 0.4  # 基本面 40%
      return score
  ```

- [ ] **機器學習選股** (進階)
  - 使用 scikit-learn 訓練模型
  - 特徵工程 (技術指標 → 特徵)
  - 預測未來漲跌機率

**預估工時:** 12-20 小時  
**優先級:** ⭐⭐ MEDIUM

---

#### 2.4 互動式圖表 ✨

**目標:** 使用 Plotly 取代靜態 matplotlib

**TODO:**
- [ ] **Plotly K 線圖**
  - 可縮放、拖曳
  - Hover 顯示詳細資訊
  - 圖表可匯出 HTML
  
  ```python
  import plotly.graph_objects as go
  
  fig = go.Figure(data=[go.Candlestick(
      x=df['date'],
      open=df['open'],
      high=df['high'],
      low=df['low'],
      close=df['close']
  )])
  fig.write_html("interactive_chart.html")
  ```

- [ ] **技術指標疊加**
  - K 線圖上疊加均線
  - 子圖顯示 RSI/MACD
  
- [ ] **回測結果互動圖**
  - 可點擊買賣點查看詳情
  - Hover 顯示當時持倉與現金

**預估工時:** 8-12 小時  
**優先級:** ⭐⭐⭐ HIGH

---

#### 2.5 通知系統整合 ✨

**TODO:**
- [ ] **Discord Webhook**
  ```python
  import requests
  
  def send_discord_alert(webhook_url, message):
      payload = {"content": message}
      requests.post(webhook_url, json=payload)
  ```

- [ ] **Telegram Bot**
  ```python
  import telegram
  
  bot = telegram.Bot(token=TOKEN)
  bot.send_message(chat_id=CHAT_ID, text="🚨 台積電突破 2000!")
  ```

- [ ] **Line Notify**
  - 簡單易用,台灣普及率高
  
- [ ] **Email 通知**
  - 使用 SMTP 發送報告
  - 附上圖表圖檔

**預估工時:** 6-10 小時  
**優先級:** ⭐⭐⭐ HIGH

---

#### 2.6 資料庫整合 ✨

**目標:** 持久化儲存,避免重複抓取

**TODO:**
- [ ] **SQLite 本地資料庫**
  - 儲存歷史價格資料
  - 儲存回測結果
  - 儲存選股結果
  
  ```sql
  CREATE TABLE stock_prices (
      stock_id TEXT,
      date DATE,
      open REAL,
      high REAL,
      low REAL,
      close REAL,
      volume INTEGER,
      PRIMARY KEY (stock_id, date)
  );
  ```

- [ ] **ORM 整合 (SQLAlchemy)**
  - 物件導向操作資料庫
  - 自動建表
  
- [ ] **PostgreSQL 支援 (可選)**
  - 生產環境使用
  - 更強的查詢效能

**預估工時:** 10-16 小時  
**優先級:** ⭐⭐ MEDIUM

---

### Phase 3: 產品化 (4-8 週)

#### 3.1 Web UI 開發 ✨

**技術選型:** FastAPI + React / Streamlit (簡單) / Dash (互動式)

**方案 A: Streamlit (最快)**
```python
import streamlit as st

st.title("台股分析器 Web 版")

stock_id = st.text_input("股票代號", "2330")
if st.button("分析"):
    data = fetch_data(stock_id)
    st.plotly_chart(create_chart(data))
```

**方案 B: FastAPI + React (專業)**
- 後端: FastAPI 提供 REST API
- 前端: React + Chart.js
- 部署: Docker + Nginx

**TODO:**
- [ ] API 設計與開發
- [ ] 前端介面設計
- [ ] 使用者認證系統
- [ ] 個人化設定儲存
- [ ] 選股清單管理
- [ ] 回測歷史紀錄

**預估工時:** 40-80 小時  
**優先級:** ⭐ LOW (Phase 3)

---

#### 3.2 自動化交易接口 ⚠️

**⚠️ 警告:** 涉及真實金錢,需謹慎開發與測試

**TODO:**
- [ ] 券商 API 研究
  - 永豐、元大等券商 API
  - 下單介面整合
  
- [ ] 模擬交易環境
  - 紙上交易 (Paper Trading)
  - 與真實 API 隔離
  
- [ ] 風險控制
  - 單日虧損上限
  - 單筆交易金額上限
  - 緊急停損機制
  
- [ ] 審計與日誌
  - 所有交易完整記錄
  - 可回溯檢查

**預估工時:** 60-100 小時  
**優先級:** ⭐ LOW (需專業金融背景)

---

#### 3.3 雲端部署 ✨

**TODO:**
- [ ] **Docker 容器化**
  ```dockerfile
  FROM python:3.9-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["python", "app.py"]
  ```

- [ ] **CI/CD 整合**
  - GitHub Actions 自動測試
  - 自動部署到伺服器
  
- [ ] **部署平台選擇**
  - Heroku (簡單)
  - AWS EC2 (彈性)
  - Google Cloud Run (容器)
  - Railway (新興平台)

**預估工時:** 12-20 小時  
**優先級:** ⭐⭐ MEDIUM

---

## 📅 執行時程表

### 近期 (1-2 週)
- [x] v1.0 核心功能完成
- [x] 單元測試建立
- [ ] **Week 1-2:** 測試覆蓋率提升至 80%
- [ ] **Week 2:** 程式碼重構 + 快取機制

### 中期 (1-2 個月)
- [ ] **Week 3-4:** 資料源擴充 (TPEX + Yahoo Finance)
- [ ] **Week 5-6:** 互動式圖表 + 通知系統
- [ ] **Week 7-8:** 資料庫整合 + 進階策略

### 長期 (3-6 個月)
- [ ] **Month 3-4:** Web UI 開發
- [ ] **Month 5-6:** 雲端部署 + 機器學習整合
- [ ] **Optional:** 自動化交易 (需額外評估)

---

## 🎯 優先級建議

### 立即執行 (本週)
1. ✅ 提升測試覆蓋率至 80%
2. ✅ 實作資料快取機制
3. ✅ 加入 Type Hints

### 短期目標 (2-4 週)
1. ✨ 互動式圖表 (Plotly)
2. ✨ Discord/Telegram 通知
3. ✨ TPEX 資料源

### 中期目標 (1-3 個月)
1. ✨ 資料庫整合 (SQLite)
2. ✨ 進階選股策略
3. ✨ 基本面資料整合

### 長期願景 (3-6 個月)
1. 🌐 Web UI
2. ☁️ 雲端部署
3. 🤖 機器學習選股

---

## 💰 成本估算

### 開發時數
- Phase 1 (優化): 26-36 小時
- Phase 2 (擴充): 60-90 小時
- Phase 3 (產品化): 112-200 小時
- **總計:** 198-326 小時

### 外部成本
- **資料源 API:**
  - TWSE/TPEX: 免費
  - Yahoo Finance: 免費 (有限制)
  - 專業資料源: $50-500/月 (可選)

- **雲端主機:**
  - Heroku Free Tier: $0
  - AWS t3.micro: ~$10/月
  - VPS (Linode/DigitalOcean): $5-20/月

- **通知服務:**
  - Discord/Telegram: 免費
  - Line Notify: 免費
  - Email: 免費 (Gmail SMTP)

**預估月費:** $0-30 (基礎方案)

---

## 🛠️ 技術棧升級建議

### 當前技術棧
```
Python 3.9 + pandas + requests + matplotlib + pytest
```

### 建議新增
```python
# 效能優化
numpy>=1.24.0
numba>=0.57.0        # JIT 編譯加速

# 資料源
yfinance>=0.2.0      # Yahoo Finance
beautifulsoup4>=4.12 # 網頁爬蟲

# 資料庫
sqlalchemy>=2.0.0    # ORM
alembic>=1.11.0      # 資料庫遷移

# 互動圖表
plotly>=5.18.0       # 已有
dash>=2.14.0         # Web dashboard (可選)

# 通知
python-telegram-bot>=20.0
discord-webhook>=1.3.0

# 型別檢查
mypy>=1.5.0
pydantic>=2.4.0

# 日誌
loguru>=0.7.0

# 設定管理
python-dotenv>=1.0.0  # 已有
pyyaml>=6.0

# 機器學習 (可選)
scikit-learn>=1.3.0
xgboost>=2.0.0

# Web 框架 (可選)
fastapi>=0.104.0
streamlit>=1.28.0
```

---

## 📝 開發規範建議

### Git Workflow
```bash
# 功能分支開發
git checkout -b feature/interactive-charts
# 開發...
git commit -m "feat: 新增 Plotly 互動式圖表"
git push origin feature/interactive-charts
# 發 PR 合併到 main
```

### Commit Message 規範
```
feat: 新增功能
fix: 修復 bug
docs: 更新文件
test: 新增測試
refactor: 重構程式碼
perf: 效能優化
chore: 雜項 (依賴更新等)
```

### 版本號規則 (Semantic Versioning)
```
v1.0.0 → v1.1.0 (新增功能,向後相容)
v1.1.0 → v1.1.1 (bug 修復)
v1.x.x → v2.0.0 (重大變更,不相容)
```

---

## 🎓 學習資源

### 技術文件
- Pandas: https://pandas.pydata.org/docs/
- Plotly: https://plotly.com/python/
- FastAPI: https://fastapi.tiangolo.com/
- pytest: https://docs.pytest.org/

### 台股資料源
- 證交所 API: https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html
- 櫃買中心: https://www.tpex.org.tw/
- FinMind (開源): https://github.com/FinMind/FinMind

### 量化交易
- QuantConnect 教學: https://www.quantconnect.com/docs/
- Backtrader: https://www.backtrader.com/

---

## ✅ 驗收標準

### Phase 1 完成標準
- [x] 測試覆蓋率 ≥ 80%
- [x] 所有測試通過
- [x] 快取機制運作正常
- [x] 資料擷取速度提升 50%+
- [x] Type Hints 覆蓋所有公開函數

### Phase 2 完成標準
- [ ] 支援 3+ 資料源
- [ ] 10+ 技術指標
- [ ] 5+ 選股策略
- [ ] 互動式圖表可用
- [ ] 通知系統整合完成

### Phase 3 完成標準
- [ ] Web UI 可正常使用
- [ ] 雲端部署成功
- [ ] 文件完整更新
- [ ] 使用手冊撰寫

---

## 🔄 持續改進

- **每週回顧:** 檢視進度,調整計畫
- **每月更新:** 更新 ROADMAP.md
- **社群回饋:** 收集使用者意見
- **技術追蹤:** 關注新工具與方法

---

**下一步行動:**
1. 選擇 Phase 1 或 Phase 2 的項目開始
2. 建立 GitHub Issues 追蹤進度
3. 設定開發環境 (安裝新依賴)
4. 開始編碼！

**問題討論:**
有任何想法或建議,歡迎提出！🦞

---

**文件版本:** v1.0  
**最後更新:** 2026-03-17  
**維護者:** Claw-Agent
