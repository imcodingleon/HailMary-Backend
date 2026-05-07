from app.domains.ai.domain.entity.paid_report import PaidReport
from app.domains.ai.domain.port.paid_report_repository_port import (
    PaidReportRepositoryPort,
)


class CreatePaidReportUseCase:
    """결제 confirm 직후 호출되는 UseCase.

    1. 동일 order_id row 이미 있으면 idempotent (그대로 반환).
    2. 같은 saju_hash + status=ready 인 결과가 있으면 chapters 복사 → ready로 즉시 마감 (캐시 hit).
    3. miss면 status=pending row만 생성. AI 호출은 별도 단계 (Phase 0 stub).
    """

    def __init__(self, *, paid_report_repo: PaidReportRepositoryPort) -> None:
        self._repo = paid_report_repo

    async def execute(self, *, order_id: str, saju_hash: str) -> PaidReport:
        existing = await self._repo.find_by_order_id(order_id)
        if existing is not None:
            return existing

        cached = await self._repo.find_ready_by_saju_hash(saju_hash)
        report = PaidReport.new_pending(order_id=order_id, saju_hash=saju_hash)
        if cached is not None:
            report.mark_ready(cached.chapters)
        return await self._repo.save(report)
