import json
from pathlib import Path

from app.services.line_service import build_daily_kpi_message

TEMPLATE_PATH = Path("app/flex_templates/daily_report.json")

SAMPLE_ROWS = [
    {"route": "2114中星", "driver": "劉嘉凱", "arrival_rate": 69.2, "ontime_rate": 100.0, "pp_rate": 100.0},
    {"route": "2131中星", "driver": "高義翔", "arrival_rate": 100.0, "ontime_rate": 90.9, "pp_rate": 100.0},
    {"route": "2132中星", "driver": "李仁達", "arrival_rate": 100.0, "ontime_rate": 0.0, "pp_rate": 100.0},
    {"route": "2814中星", "driver": "劉嘉凱", "arrival_rate": 25.0, "ontime_rate": 100.0, "pp_rate": 100.0},
    {"route": "2831中星", "driver": "蔣瑋溙", "arrival_rate": 100.0, "ontime_rate": 80.0, "pp_rate": 100.0},
    {"route": "2832中星", "driver": "邱昱凱", "arrival_rate": 0.0, "ontime_rate": 100.0, "pp_rate": 100.0},
    {"route": "2833中星", "driver": "陳偉峰", "arrival_rate": 100.0, "ontime_rate": 100.0, "pp_rate": 100.0},
]


def test_template_json_valid():
    assert TEMPLATE_PATH.exists()
    data = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    assert data["type"] == "bubble"


def test_build_message_returns_flex():
    msg = build_daily_kpi_message(SAMPLE_ROWS, "115/5/20")
    assert msg.alt_text == "中星 KPI 戰報 115/5/20"
    bubble = msg.contents
    assert bubble["type"] == "bubble"


def test_low_rate_marked():
    msg = build_daily_kpi_message(SAMPLE_ROWS, "115/5/20")
    body_text = json.dumps(msg.contents)
    assert "⚠️" in body_text
    assert "#5c0000" in body_text


def test_only_zhongxing_rows():
    mixed = SAMPLE_ROWS + [
        {"route": "2001摩爾", "driver": "外部司機", "arrival_rate": 50.0, "ontime_rate": 50.0, "pp_rate": 50.0}
    ]
    filtered = [r for r in mixed if "中星" in r["route"]]
    msg = build_daily_kpi_message(filtered, "115/5/20")
    body_text = json.dumps(msg.contents)
    assert "外部司機" not in body_text
