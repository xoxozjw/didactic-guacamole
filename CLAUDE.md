# CLAUDE.md

本文件为 AI 助手（如 Claude Code）提供此代码库的结构说明、开发工作流与关键约定。

---

## 项目概述

本项目是一个基于 **FastAPI** 的 LINE Bot 后端服务，主要功能包括：

- 接收 LINE Webhook 事件
- 生成并推送 **LINE Flex Message**（当日战报、月平均报表两种模板）
- 整合 **Google Sheets API**（读取/写入数据）
- 整合 **Google Vision API**（图像识别/OCR）

---

## 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.11+ | 主要开发语言 |
| FastAPI | Web 框架，提供异步路由 |
| uvicorn | ASGI 服务器 |
| line-bot-sdk | LINE Messaging API 封装 |
| google-api-python-client | Google Sheets 集成 |
| google-cloud-vision | Google Vision API 集成 |
| pytest | 单元测试框架 |
| python-dotenv | 环境变量管理 |

---

## 目录结构

```
didactic-guacamole/
├── app/
│   ├── main.py                  # FastAPI 应用入口，注册路由
│   ├── routers/
│   │   ├── webhook.py           # LINE Webhook 接收路由
│   │   └── reports.py           # 报表触发路由
│   ├── services/
│   │   ├── line_service.py      # LINE Bot 消息推送逻辑
│   │   ├── sheets_service.py    # Google Sheets 读写逻辑
│   │   └── vision_service.py    # Google Vision OCR 逻辑
│   ├── flex_templates/
│   │   ├── daily_report.json    # 当日战报 Flex Message 模板
│   │   └── monthly_avg.json     # 月平均战报 Flex Message 模板
│   └── models/
│       └── schemas.py           # Pydantic 数据模型
├── tests/
│   ├── test_webhook.py
│   ├── test_sheets_service.py
│   └── test_flex_templates.py
├── .env.example                 # 环境变量示例（不含真实密钥）
├── requirements.txt
└── CLAUDE.md
```

---

## 开发工作流

### 安装依赖

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填写以下必要字段（见下方环境变量说明）
```

### 启动开发服务器

```bash
uvicorn app.main:app --reload --port 8000
```

### 运行测试

```bash
pytest
pytest tests/test_webhook.py -v   # 单个文件
```

---

## 环境变量

| 变量名 | 说明 |
|--------|------|
| `LINE_CHANNEL_SECRET` | LINE Bot Channel Secret |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot Channel Access Token |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Service Account JSON 文件路径 |
| `SPREADSHEET_ID` | Google Sheets 表格 ID |

> **重要**：`.env` 文件永远不应提交到版本库。

---

## 关键约定

### FastAPI 路由

- 所有路由函数使用 `async def`
- 路由按功能拆分到 `app/routers/` 下的独立文件
- 在 `app/main.py` 中使用 `app.include_router()` 注册

```python
# 示例
@router.post("/webhook")
async def webhook(request: Request):
    ...
```

### LINE Flex Message

- JSON 模板统一存放在 `app/flex_templates/` 目录，**不内联**在 Python 代码中
- 模板遵循 LINE 官方 Flex Message schema，顶层类型为 `bubble` 或 `carousel`
- 动态数据通过字符串替换或 `dict` 合并注入模板
- 两种核心模板：
  - `daily_report.json`：当日战报（含当日数据对比）
  - `monthly_avg.json`：月平均报表（含趋势统计）

### Google Sheets 服务

- 认证使用 Service Account，路径通过 `GOOGLE_APPLICATION_CREDENTIALS` 指定
- 封装在 `app/services/sheets_service.py`，路由层不直接调用 Google API

### Google Vision 服务

- OCR 功能封装在 `app/services/vision_service.py`
- 仅处理图像字节流，不依赖本地文件路径

### 代码风格

- 使用 `black` 格式化（行宽 88）
- 使用 `ruff` 做 lint 检查
- 类型注解：所有函数参数与返回值必须标注类型

---

## AI 助手注意事项

1. **不要将 API 密钥或 token 硬编码**到任何源文件中，一律通过 `os.getenv()` 读取。
2. 生成 Flex Message JSON 时，严格遵循 [LINE Flex Message 官方文档](https://developers.line.biz/en/docs/messaging-api/flex-message-elements/) 的 schema。
3. FastAPI 路由签名中使用 Pydantic 模型作为请求体类型，不要使用裸 `dict`。
4. 修改 `flex_templates/` 中的 JSON 前，先确认 LINE Bot SDK 版本支持该属性。
5. Google API 调用均为网络 I/O，务必使用异步封装或在线程池中执行，避免阻塞事件循环。
6. 新增功能时优先在 `services/` 层实现业务逻辑，路由层只做参数校验与响应组装。
