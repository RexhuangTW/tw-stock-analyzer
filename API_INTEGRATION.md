# 永豐 API 整合方案 (2026-03-30)

## 決策：混合策略 (選項 C)

### 資料來源分工

| 用途 | API | 原因 |
|------|-----|------|
| 選股系統 | Yahoo Finance | • 有日線資料<br>• 無查詢限制<br>• 批次查詢快速<br>• 已整合完善 |
| 即時監控 | 永豐 API | • 即時報價（無延遲）<br>• 查詢實際持倉<br>• 整張+零股完整支援 |

---

## 永豐 API 限制

### 發現的問題
1. **只有分鐘線，無日線**
   - `api.kbars()` 回傳分鐘 K 線
   - 無法直接取得日線資料
   - 需自行聚合（不切實際）

2. **交易時段查詢限制**
   - K 線查詢：最多 270 次
   - 5 秒內最多 50 次請求
   - **掃描 1,080 檔會超限**

3. **Kbars 物件結構**
   ```python
   # 不是 list，是特殊物件
   kbars.ts      # list of timestamps
   kbars.Open    # list of open prices
   kbars.High    # list of high prices
   kbars.Low     # list of low prices
   kbars.Close   # list of close prices
   kbars.Volume  # list of volumes
   ```

---

## 實作成果

### ✅ 已完成

#### 1. 永豐 API 基礎整合
- `sinopac_config.py` - API 設定管理
- `sinopac_fetcher.py` - 資料抓取模組（未用於選股）
- 憑證管理：`.certs/sinopac.pfx`

#### 2. 持倉監控系統
- `sinopac_monitor.py` - 完整監控腳本
- **功能**：
  - 即時報價查詢
  - 實際持倉查詢（整張+零股）
  - 損益計算
  - 停損/停利警示
  - 觀察名單進場提醒

#### 3. 零股查詢解決
```python
# 關鍵：必須指定 unit=Unit.Share
positions = api.list_positions(
    api.stock_account,
    unit=sj.constant.Unit.Share  # 以「股」為單位
)
```

**API 行為**：
- `unit=Unit.Common`（預設）：只回傳整張（張數）
- `unit=Unit.Share`：回傳全部（股數，包含零股）

---

## 性能測試

### 即時報價（snapshots）
- 10 檔：瞬間完成
- 50 檔：0.04 秒（1 ms/檔）
- **推估 1,080 檔**：約 1-2 秒

**對比 yfinance**：
- yfinance 選股：5-10 分鐘（1,080 檔）
- 永豐 snapshots：1-2 秒（快 150-300 倍）
- **但**：只有即時報價，無歷史資料

---

## 檔案清單

### 核心檔案
```
tw-stock-analyzer/
├── sinopac_config.py          # API 設定
├── sinopac_monitor.py         # 持倉監控主程式
├── .env                       # 環境變數（API Key）
├── .certs/
│   └── sinopac.pfx           # 憑證檔案
└── src/data/
    └── sinopac_fetcher.py    # 資料抓取模組（備用）
```

### 環境變數（.env）
```bash
SINOPAC_API_KEY=...
SINOPAC_SECRET_KEY=...
SINOPAC_PERSON_ID=F128099494
SINOPAC_CA_CERT_PATH=.certs/sinopac.pfx
SINOPAC_CA_PASSWORD=F128099494
```

---

## 使用方式

### 持倉監控
```bash
cd tw-stock-analyzer
python3 sinopac_monitor.py
```

**輸出**：
- 實際持倉（從證券帳戶查詢）
- 即時價格與損益
- 停損/停利警示
- 觀察名單進場機會

### 整合到每日報告
```python
from sinopac_monitor import SinopacMonitor

with SinopacMonitor() as monitor:
    # 查詢持倉
    positions = monitor.api.list_positions(
        monitor.api.stock_account,
        unit=sj.constant.Unit.Share
    )
    
    # 即時報價
    codes = ['2330', '2454', '2317']
    contracts = [monitor.api.Contracts.Stocks[c] for c in codes]
    snapshots = monitor.api.snapshots(contracts)
```

---

## 自動化排程

### 現有 cron jobs
- **08:30 盤前選股**：使用 yfinance
- **14:45 盤後更新**：使用 yfinance

### 建議新增
- **盤中監控**（選用）：每 30 分鐘查詢持倉，檢查停損/停利
- **即時警示**：達到進場價、觸發停損時通知

---

## 未來優化

### 短期
1. 整合永豐 API 到每日報告（持倉即時價格）
2. 設定停損/停利自動警示
3. 觀察名單即時監控（達到進場價通知）

### 中期
1. 盤中自動監控（每 30 分鐘）
2. 整合到 n8n workflow
3. 交易訊號推播（Discord/Telegram）

### 長期（如有需要）
1. 自動下單功能（需審慎評估）
2. 回測系統整合永豐歷史資料
3. 多帳戶管理

---

## 技術筆記

### Context Manager 使用
```python
from sinopac_fetcher import SinopacFetcher

# 自動登入/登出
with SinopacFetcher() as fetcher:
    df = fetcher.get_snapshot(['2330', '2454'])
    # 離開時自動登出
```

### 錯誤處理
- SIGSEGV 錯誤：Shioaji 內部清理問題，可忽略
- 程式功能正常，exit code 不影響

### 查詢限制
- 交易時段：K 線最多 270 次/5 秒內 50 次
- 非交易時段：無限制
- **建議**：盤後/盤前做大量查詢

---

## 總結

**最終方案**：
- ✅ 選股系統：保留 yfinance（成熟、快速、無限制）
- ✅ 即時監控：永豐 API（即時、準確、含零股）
- ✅ 最佳平衡：發揮各自優勢

**核心成果**：
- 永豐 API 整合完成（持倉監控）
- 零股查詢問題解決
- 系統架構清晰、可維護

**後續工作**：
- 整合到每日報告
- 設定自動警示
- 優化監控頻率
