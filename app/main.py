import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routers import reports, webhook  # noqa: E402

app = FastAPI(title="中星運輸 KPI LINE Bot")
app.include_router(webhook.router)
app.include_router(reports.router)
