from pydantic import BaseModel, Field


class KpiRow(BaseModel):
    route: str
    driver: str
    arrival_rate: float = Field(ge=0, le=100)
    ontime_rate: float = Field(ge=0, le=100)
    pp_rate: float = Field(ge=0, le=100)


class DailyReportRequest(BaseModel):
    to: str
    date: str | None = None
