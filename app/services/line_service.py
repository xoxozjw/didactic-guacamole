from __future__ import annotations

import os
from typing import Any

from linebot import LineBotApi
from linebot.models import FlexSendMessage

_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN", ""))

_BG_ROOT = "#0d1117"
_BG_HEADER_COL = "#2a2a40"
_BG_LOW = "#5c0000"
_BG_NORMAL = "#1e1e2e"
_COLOR_GOLD = "#ffd700"
_COLOR_GREEN = "#00cc66"
_COLOR_RED = "#ff6666"
_COLOR_WHITE = "#ffffff"
_COLOR_GRAY = "#aaaaaa"
_COLOR_DIM = "#555555"
_COLOR_SUB = "#888888"
_THRESHOLD = 90.0


def _col_header(title: str) -> dict[str, Any]:
    return {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": _BG_HEADER_COL,
        "cornerRadius": "8px",
        "paddingAll": "8px",
        "flex": 1,
        "contents": [
            {"type": "text", "text": title, "color": _COLOR_GOLD, "size": "sm",
             "weight": "bold", "align": "center"},
            {"type": "text", "text": "司機　率", "color": _COLOR_GRAY, "size": "xxs",
             "align": "center"},
        ],
    }


def _cell(driver: str, rate: float) -> dict[str, Any]:
    low = rate < _THRESHOLD
    return {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": _BG_LOW if low else _BG_NORMAL,
        "cornerRadius": "8px",
        "paddingAll": "8px",
        "flex": 1,
        "contents": [
            {"type": "text", "text": driver, "color": _COLOR_WHITE, "size": "sm",
             "weight": "bold", "align": "center", "wrap": True},
            {"type": "text",
             "text": f"{rate:.1f}% ⚠️" if low else f"{rate:.1f}%",
             "color": _COLOR_RED if low else (_COLOR_GREEN if rate == 100.0 else _COLOR_WHITE),
             "size": "sm", "align": "center"},
        ],
    }


def _data_row(cells: list[dict[str, Any]]) -> dict[str, Any]:
    return {"type": "box", "layout": "horizontal", "spacing": "sm",
            "margin": "sm", "contents": cells}


def build_daily_kpi_message(rows: list[dict], date: str) -> FlexSendMessage:
    """
    rows: list of {"route": str, "driver": str,
                   "arrival_rate": float, "ontime_rate": float, "pp_rate": float}
         已過濾為中星路線，本函數不再過濾。
    date: 顯示用日期字串，e.g. "115/5/20"
    """
    by_arrival = sorted(rows, key=lambda r: r["arrival_rate"])
    by_ontime = sorted(rows, key=lambda r: r["ontime_rate"])
    by_pp = sorted(rows, key=lambda r: r["pp_rate"])

    n = len(rows)
    grid_rows: list[dict[str, Any]] = []
    for i in range(n):
        grid_rows.append(
            _data_row([
                _cell(by_arrival[i]["driver"], by_arrival[i]["arrival_rate"]),
                _cell(by_ontime[i]["driver"], by_ontime[i]["ontime_rate"]),
                _cell(by_pp[i]["driver"], by_pp[i]["pp_rate"]),
            ])
        )

    contents: list[dict[str, Any]] = [
        {
            "type": "box",
            "layout": "horizontal",
            "spacing": "md",
            "alignItems": "center",
            "contents": [
                {"type": "text", "text": "⭐", "size": "xxl", "flex": 0, "gravity": "center"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "中星運輸 KPI", "color": _COLOR_GREEN,
                         "size": "sm", "weight": "bold"},
                        {"type": "text", "text": "最新單日 KPI", "color": _COLOR_WHITE,
                         "size": "xl", "weight": "bold"},
                    ],
                },
            ],
        },
        {"type": "text", "text": f"日期：{date} ｜ 表現較低者置頂",
         "color": _COLOR_SUB, "size": "xs", "margin": "sm"},
        {"type": "separator", "color": "#333333", "margin": "sm"},
        {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "margin": "sm",
            "contents": [
                _col_header("到店率"),
                _col_header("準時率"),
                _col_header("PP率"),
            ],
        },
        *grid_rows,
        {"type": "separator", "color": "#333333", "margin": "md"},
        {"type": "text", "text": "升冪排序　｜　低於 90% 自動標示 ⚠️",
         "color": _COLOR_DIM, "size": "xxs", "align": "center", "margin": "sm"},
    ]

    bubble: dict[str, Any] = {
        "type": "bubble",
        "size": "giga",
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": _BG_ROOT,
            "paddingAll": "16px",
            "spacing": "sm",
            "contents": contents,
        },
    }

    return FlexSendMessage(alt_text=f"中星 KPI 戰報 {date}", contents=bubble)


async def push_daily_kpi(to: str, rows: list[dict], date: str) -> None:
    import asyncio
    msg = build_daily_kpi_message(rows, date)
    await asyncio.to_thread(_api.push_message, to, msg)
