from dataclasses import dataclass, field
from datetime import datetime

from app.domains.ai.domain.value_object.report_status import ReportStatus


@dataclass
class PaidReport:
    """유료 리포트 엔티티.

    만료는 별도 컬럼으로 관리하지 않는다. order_id로 연결된 Payment.expires_at 참조.
    chapters: 12 페이지 결과를 페이지 식별자(예: "P-0", "P-1") → 본문 텍스트로 매핑.
    """

    order_id: str
    saju_hash: str
    status: ReportStatus
    chapters: dict[str, str] = field(default_factory=dict)
    created_at: datetime | None = None

    @classmethod
    def new_pending(cls, *, order_id: str, saju_hash: str) -> "PaidReport":
        return cls(
            order_id=order_id,
            saju_hash=saju_hash,
            status=ReportStatus.PENDING,
            chapters={},
        )

    def mark_ready(self, chapters: dict[str, str]) -> None:
        self.chapters = dict(chapters)
        self.status = ReportStatus.READY
