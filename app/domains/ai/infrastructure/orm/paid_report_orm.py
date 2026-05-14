from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domains.ai.domain.value_object.report_status import ReportStatus
from app.infrastructure.database.session import Base


class PaidReportORM(Base):
    __tablename__ = "paid_reports"

    order_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    saju_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    # 재접속 토큰 (UUID4 hex 32자) — 이메일 링크에 사용. order_id 노출 방지.
    share_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    chapters: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
