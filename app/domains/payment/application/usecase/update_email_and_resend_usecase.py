"""결제 완료 후 사용자가 결과지 받을 이메일을 수정한 경우 처리.

흐름:
1. PayApp webhook(`/feedback`)이 이미 PaidReport 합성 트리거 + 메일 발송 진행
2. FE success 페이지에서 이메일 확인 모달 → "수정" → 본 UseCase 호출
3. Payment.customer_email 업데이트 + PaidReport.share_code 조회 → 새 주소에 재발송
"""

from __future__ import annotations

import logging

from app.domains.payment.application.payment_ports import (
    EmailResendPort,
    PaidReportShareLookupPort,
)
from app.domains.payment.domain.port.payment_repository_port import (
    PaymentRepositoryPort,
)

logger = logging.getLogger(__name__)


class UpdateEmailAndResendUseCase:
    def __init__(
        self,
        *,
        payment_repo: PaymentRepositoryPort,
        share_lookup: PaidReportShareLookupPort,
        email_resend: EmailResendPort,
    ) -> None:
        self._payment_repo = payment_repo
        self._share_lookup = share_lookup
        self._email_resend = email_resend

    async def execute(self, *, order_id: str, new_email: str) -> None:
        updated = await self._payment_repo.update_customer_email(
            order_id=order_id,
            new_email=new_email,
        )
        if updated is None:
            raise ValueError("결제 정보를 찾을 수 없습니다.")

        share_code = await self._share_lookup.find_share_code(order_id)
        if share_code is None:
            # PaidReport 합성이 아직 끝나지 않은 케이스 — 메일 수정만 반영하고 종료.
            # 합성 완료 시 자동 발송 단계에서 업데이트된 이메일이 사용됨.
            logger.info(
                "[update-email] paid report not ready yet for order=%s — email updated only",
                order_id,
            )
            return

        try:
            await self._email_resend.execute(
                to=new_email,
                share_code=share_code,
                character=updated.character.value,
                expires_at=updated.expires_at,
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("[update-email] resend failed for order=%s: %s", order_id, e)
