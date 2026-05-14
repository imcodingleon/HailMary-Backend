import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domains.ai.domain.value_object.report_status import ReportStatus


@dataclass
class PaidReport:
    """유료 리포트 엔티티.

    만료는 별도 컬럼으로 관리하지 않는다. order_id로 연결된 Payment.expires_at 참조.
    chapters: 12 페이지 결과를 페이지 식별자("p0", "p1", ..., "p10") →
              페이지별 데이터 dict (PaidChapterPN.model_dump() 결과)로 매핑.
              저장 시 JSON 컬럼에 통째 직렬화됨.
    share_code: 비로그인 사용자 재접속 URL용 UUID4 hex (32자).
                order_id 노출 방지 (토스 결제 키 추측 어려움 X). 이메일 링크에 사용.
    """

    order_id: str
    saju_hash: str
    status: ReportStatus
    share_code: str = field(default_factory=lambda: uuid.uuid4().hex)
    chapters: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None

    @classmethod
    def new_pending(cls, *, order_id: str, saju_hash: str) -> "PaidReport":
        return cls(
            order_id=order_id,
            saju_hash=saju_hash,
            status=ReportStatus.PENDING,
            share_code=uuid.uuid4().hex,
            chapters={},
        )

    def mark_ready(self, chapters: dict[str, Any]) -> None:
        self.chapters = dict(chapters)
        self.status = ReportStatus.READY
