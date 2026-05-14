"""결과지 재접속 링크 이메일 발송 UseCase.

호출 시점: PaidReport ready 직후 (CreatePaidReportUseCase 내부 또는 ConfirmPaymentUseCase).
fire-and-forget — 실패해도 PaidReport는 ready 유지 (사용자가 결제 후 redirect로 결과 접근 가능).
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from app.domains.ai.domain.templates.email_templates import build_result_link_email

if TYPE_CHECKING:
    from app.infrastructure.external.ses.client import SESClient

logger = logging.getLogger(__name__)


class SendResultLinkEmailUseCase:
    """share_code 기반 결과지 링크를 이메일로 발송."""

    def __init__(self, *, ses_client: SESClient, base_url: str) -> None:
        self._ses = ses_client
        self._base_url = base_url

    async def execute(
        self,
        *,
        to: str,
        share_code: str,
        character: str,
        expires_at: datetime,
    ) -> None:
        """이메일 1통 발송.

        실패 시 로그만 남기고 예외 swallow (fire-and-forget).
        """
        subject, html_body, text_body = build_result_link_email(
            share_code=share_code,
            character=character,
            expires_at=expires_at,
            base_url=self._base_url,
        )
        try:
            await self._ses.send_email(
                to=to,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )
            logger.info("result link email sent (to=%s, share_code=%s)", to, share_code)
        except Exception:
            logger.exception(
                "result link email failed (to=%s, share_code=%s) — swallowed",
                to,
                share_code,
            )
