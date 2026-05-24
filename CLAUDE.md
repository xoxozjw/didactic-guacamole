# CLAUDE.md

本文件為 AI 助手（如 Claude Code）提供此代碼庫的結構說明、開發工作流與關鍵約定。

---

## 專案概述

本專案是一個基於 **FastAPI** 的 LINE Bot 後端服務（中星運輸 KPI 系統），主要功能：

- 接收 LINE Webhook 事件
- 從 **Google Sheets** 讀取每日路線 KPI 數據（到店率、準時率、PP 率）
- **僅顯示路線名稱包含「中星」的記錄**
- 生成並推送 **LINE Flex Message**（深色主題格狀 KPI 戰報）
- 整合 **Google Vision API**（圖像 OCR）

---

## 技術棧

| 技術 | 用途 |
|------|------|
| Python 3.11+ | 主要開發語言 |
| FastAPI | Web 框架，提供非同步路由 |
| uvicorn | ASGI 伺服器 |
| line-bot-sdk | LINE Messaging API 封裝 |
| google-api-python-client | Google Sheets 整合 |
| google-cloud-vision | Google Vision API 整合 |
| pytest | 單元測試框架 |
| python-dotenv | 環境變數管理 |

---

## 目錄結構

```
didactic-guacamole/
├── app/
│   ├── main.py                      # FastAPI 應用入口，註冊路由
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── webhook.py               # LINE Webhook 接收路由
│   │   └── reports.py               # 報表觸發路由（手動 / 排程）
│   ├── services/
│   │   ├── __init__.py
│   │   ├── line_service.py          # Flex Message 建構 + LINE API 推送
│   │   ├── sheets_service.py        # Google Sheets 讀寫（含中星過濾）
│   │   └── vision_service.py        # Google Vision OCR
│   ├── flex_templates/
│   │   ├── daily_report.json        # 當日 KPI 戰報 Flex Message 輸出範例
│   │   └── monthly_avg.json         # 月平均報表 Flex Message 輸出範例
│   └── models/
│       ├── __init__.py
│       └── schemas.py               # Pydantic 資料模型
├── tests/
│   ├── __init__.py
│   ├── test_webhook.py
│   ├── test_sheets_service.py
│   └── test_flex_templates.py
├── .env.example
├── requirements.txt
└── CLAUDE.md
```

---

## 開發工作流

### 安裝依賴

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 配置環境變數

```bash
cp .env.example .env
# 填寫 LINE_CHANNEL_SECRET、LINE_CHANNEL_ACCESS_TOKEN、GOOGLE_APPLICATION_CREDENTIALS、SPREADSHEET_ID
```

### 啟動開發伺服器

```bash
uvicorn app.main:app --reload --port 8000
```

### 運行測試

```bash
pytest
pytest tests/test_webhook.py -v
```

---

## 環境變數

| 變數名 | 說明 |
|--------|------|
| `LINE_CHANNEL_SECRET` | LINE Bot Channel Secret |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot Channel Access Token |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Service Account JSON 文件路徑 |
| `SPREADSHEET_ID` | Google Sheets 表格 ID |

> `.env` 文件永遠不應提交到版本庫。

---

## 關鍵約定

### FastAPI 路由

- 所有路由函數使用 `async def`
- 路由按功能拆分到 `app/routers/` 獨立文件
- 在 `app/main.py` 使用 `app.include_router()` 註冊

### LINE Flex Message（核心功能）

`app/flex_templates/` 內的 JSON 為**輸出範例**（測試 / 參考用），**不作為注入模板**。

**實際訊息由 `line_service.build_daily_kpi_message()` 完全動態建構。**

#### 樣式規範

| 元素 | 色碼 |
|------|------|
| 背景 | `#0d1117` |
| 欄位標題底色 | `#2a2a40` |
| 欄位標題文字（金色） | `#ffd700` |
| 低於 90%（紅底） | `#5c0000` |
| 低於 90% 文字 | `#ff6666` |
| 100%（深底） | `#1e1e2e` |
| 100% 文字（綠色） | `#00cc66` |
| 一般達標文字 | `#ffffff` |

#### 排版規則

- 三欄格狀：到店率 / 準時率 / PP 率
- 各欄**獨立升冪排序**（低 → 高）
- 低於 90% 自動加 `⚠️` 警示、紅底標示
- 僅顯示路線名稱含「中星」的記錄

#### 建構流程

```
sheets_service.get_daily_kpi()
  → 篩選 "中星" in route_name
  → 各欄升冪排序
  → line_service.build_daily_kpi_message(rows, date)
  → LineBotApi.push_message()
```

### Google Sheets 服務

- 認證使用 Service Account（`GOOGLE_APPLICATION_CREDENTIALS` 指定路徑）
- 封裝在 `sheets_service.py`，路由層不直接呼叫 Google API
- 每筆資料結構：
  ```python
  {"route": str, "driver": str, "arrival_rate": float, "ontime_rate": float, "pp_rate": float}
  ```

### Google Vision 服務

- OCR 封裝在 `vision_service.py`，僅接受圖像 bytes，不依賴本地文件路徑

### 程式碼風格

- `black` 格式化（行寬 88）
- `ruff` lint 檢查
- 所有函數參數與返回值必須標注類型

---

## AI 助手注意事項

1. **禁止硬編碼 API 金鑰**，一律通過 `os.getenv()` 讀取。
2. Flex Message 樣式改動請修改 `line_service.py` 中的輔助函數，不要改 JSON 範例文件。
3. **過濾邏輯**在 `sheets_service.py` 執行（`"中星" in row["route"]`），`line_service` 收到的已是過濾後資料。
4. 各欄排序為**獨立升冪**，非整體綜合排序。
5. Google API 呼叫須用 `asyncio.to_thread()` 包裝，避免阻塞事件循環。
6. 業務邏輯在 `services/` 層實現，路由層只做參數校驗與回應組裝。
