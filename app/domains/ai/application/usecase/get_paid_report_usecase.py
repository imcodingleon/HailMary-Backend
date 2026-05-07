from datetime import UTC, datetime

from app.domains.ai.domain.entity.paid_report import PaidReport
from app.domains.ai.domain.port.paid_report_repository_port import (
    PaidReportRepositoryPort,
)
from app.domains.ai.domain.value_object.report_status import ReportStatus
from app.domains.payment.domain.entity.payment import Payment
from app.domains.payment.domain.port.payment_repository_port import (
    PaymentRepositoryPort,
)


class PaidReportNotFoundError(Exception):
    """order_id에 해당하는 PaidReport 또는 Payment가 없을 때."""


class PaidReportExpiredError(Exception):
    """Payment.expires_at이 지났을 때 (HTTP 410)."""


class GetPaidReportUseCase:
    """결제 만료 체크 + 결과 조회.

    만료 정책: ai 도메인은 expires_at을 갖지 않는다. Payment.expires_at이 SSOT.
    """

    def __init__(
        self,
        *,
        paid_report_repo: PaidReportRepositoryPort,
        payment_repo: PaymentRepositoryPort,
    ) -> None:
        self._paid_report_repo = paid_report_repo
        self._payment_repo = payment_repo

    async def execute(self, order_id: str) -> tuple[PaidReport, Payment]:
        report = await self._paid_report_repo.find_by_order_id(order_id)
        if report is None:
            raise PaidReportNotFoundError(order_id)

        payment = await self._payment_repo.find_by_order_id(order_id)
        if payment is None:
            raise PaidReportNotFoundError(order_id)

        now = datetime.now(UTC)
        if now >= payment.expires_at:
            report.status = ReportStatus.EXPIRED
            raise PaidReportExpiredError(order_id)

        return report, payment
