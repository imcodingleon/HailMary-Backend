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
from app.domains.user.domain.entity.user import User
from app.domains.user.domain.port.user_repository_port import UserRepositoryPort


class PaidReportNotFoundError(Exception):
    """order_id에 해당하는 PaidReport 또는 Payment가 없을 때."""


class PaidReportExpiredError(Exception):
    """Payment.expires_at이 지났을 때 (HTTP 410)."""


class GetPaidReportUseCase:
    """결제 만료 체크 + 결과 조회 + 분석용 user 동봉.

    만료 정책: ai 도메인은 expires_at을 갖지 않는다. Payment.expires_at이 SSOT.
    User 조회 실패는 결과지 응답을 막지 않음 (분석 메타에 그치므로 None 허용).
    """

    def __init__(
        self,
        *,
        paid_report_repo: PaidReportRepositoryPort,
        payment_repo: PaymentRepositoryPort,
        user_repo: UserRepositoryPort,
    ) -> None:
        self._paid_report_repo = paid_report_repo
        self._payment_repo = payment_repo
        self._user_repo = user_repo

    async def execute(self, order_id: str) -> tuple[PaidReport, Payment, User | None]:
        report = await self._paid_report_repo.find_by_order_id(order_id)
        if report is None:
            raise PaidReportNotFoundError(order_id)
        return await self._verify_and_return(report)

    async def execute_by_share_code(
        self, share_code: str
    ) -> tuple[PaidReport, Payment, User | None]:
        """share_code(UUID4 hex)로 PaidReport 조회 — 이메일 재접속 링크 진입점."""
        report = await self._paid_report_repo.find_by_share_code(share_code)
        if report is None:
            raise PaidReportNotFoundError(share_code)
        return await self._verify_and_return(report)

    async def _verify_and_return(
        self, report: PaidReport
    ) -> tuple[PaidReport, Payment, User | None]:
        """Payment 존재 + expires_at 체크 후 (report, payment, user) 반환."""
        payment = await self._payment_repo.find_by_order_id(report.order_id)
        if payment is None:
            raise PaidReportNotFoundError(report.order_id)

        # MySQL DATETIME은 tzinfo 없이 저장되므로 naive로 로드됨 → aware now와 비교 불가.
        # 저장 정책상 UTC로 박혀 있으므로 비교 시 UTC tzinfo 부여.
        expires_at = payment.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)

        now = datetime.now(UTC)
        if now >= expires_at:
            report.status = ReportStatus.EXPIRED
            raise PaidReportExpiredError(report.order_id)

        user = await self._user_repo.find_by_id(payment.user_id)
        return report, payment, user
