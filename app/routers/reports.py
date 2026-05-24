from __future__ import annotations

import asyncio
from datetime import date

from fastapi import APIRouter

from app.services import line_service, sheets_service

router = APIRouter(prefix="/reports")


@router.post("/daily")
async def trigger_daily_report(to: str) -> dict:
    rows = await asyncio.to_thread(sheets_service.get_daily_kpi)
    today = date.today().strftime("%Y/%m/%d")
    await line_service.push_daily_kpi(to, rows, today)
    return {"status": "sent", "rows": len(rows)}
