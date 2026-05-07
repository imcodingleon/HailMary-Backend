from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaidReportStatusResponse(BaseModel):
    """`GET /api/saju/paid/{order_id}/status` 응답."""

    model_config = ConfigDict(populate_by_name=True)

    status: str  # "pending" | "ready" | "expired"


class PaidReportResponse(BaseModel):
    """`GET /api/saju/paid/{order_id}` 응답 — 12 페이지 결과."""

    model_config = ConfigDict(populate_by_name=True)

    order_id: str
    status: str
    chapters: dict[str, str]
    expires_at: datetime
