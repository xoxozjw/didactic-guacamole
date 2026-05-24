from __future__ import annotations

import os
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
_SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")


def _get_service() -> Any:
    creds = service_account.Credentials.from_service_account_file(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""), scopes=_SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def get_daily_kpi(sheet_range: str = "工作表1!A2:K") -> list[dict]:
    """
    從 Google Sheets 讀取當日 KPI，僅回傳路線含「中星」的記錄。
    欄位順序假設為：路線, 應到, 實到, 到店率, 遲送, 早送, 準時率, 應刷, 實刷, PP率, 物流士
    """
    service = _get_service()
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=_SPREADSHEET_ID, range=sheet_range)
        .execute()
    )
    rows = result.get("values", [])

    records: list[dict] = []
    for row in rows:
        if len(row) < 11:
            continue
        route = row[0]
        if "中星" not in route:
            continue
        try:
            records.append({
                "route": route,
                "driver": row[10],
                "arrival_rate": _pct(row[3]),
                "ontime_rate": _pct(row[6]),
                "pp_rate": _pct(row[9]),
            })
        except (ValueError, IndexError):
            continue
    return records


def _pct(value: str) -> float:
    return float(value.strip().replace("%", ""))
