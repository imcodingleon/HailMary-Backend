"""PayApp webhook(feedbackurl) 처리 UseCase.

PayApp → BE 호출. linkkey/linkval/price 검증 후 pay_state 별로 payment 상태 갱신.
결제완료(pay_state=4) 시 PaidReport 합성 + Amplitude 트래킹.
멱등성: 같은 (order_id, pay_state) 중복 처리 방지.
응답은 반드시 텍스트 "SUCCESS" (HTTP 200) — checkretry=y 라 SUCCESS 아니면 PayApp이 10회 재시도.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from app.domains.payment.application.payment_ports import (
    PaidReportCreatorPort,
    SajuHashResolverPort,
    UserDemographicsPort,
    safe_track_payment_completed,
)
from app.domains.payment.domain.port.analytics_port import AnalyticsPort
from app.domains.payment.domain.port.payment_repository_port import (
    PaymentRepositoryPort,
)
from app.domains.payment.domain.value_object.payment_status import PaymentStatus

logger = logging.getLogger(__name__)

# PayApp pay_state 코드 → 우리 PaymentStatus 매핑
_PAY_STATE_TO_STATUS: dict[str, PaymentStatus] = {
    "1": PaymentStatus.READY,
    "4": PaymentStatus.DONE,
    "8": PaymentStatus.ABORTED,
    "32": PaymentStatus.ABORTED,
    "9": PaymentStatus.CANCELED,
    "64": PaymentStatus.CANCELED,
    "10": PaymentStatus.WAITING_FOR_DEPOSIT,
    "70": PaymentStatus.PARTIAL_CANCELED,
    "71": PaymentStatus.PARTIAL_CANCELED,
}


class FeedbackResult:
    """webhook 처리 결과. router는 모두 "SUCCESS" 텍스트로 응답."""

    def __init__(self, *, ok: bool, reason: str = "") -> None:
        self.ok = ok
        self.reason = reason


class HandlePayAppFeedbackUseCase:
    def __init__(
        self,
        *,
        repo: PaymentRepositoryPort,
        expected_linkkey: str,
        expected_linkval: str,
        paid_report_creator: PaidReportCreatorPort | None = None,
        saju_hash_resolver: SajuHashResolverPort | None = None,
        analytics: AnalyticsPort | None = None,
        user_demographics: UserDemographicsPort | None = None,
    ) -> None:
        self._repo = repo
        self._expected_linkkey = expected_linkkey
        self._expected_linkval = expected_linkval
        self._paid_report_creator = paid_report_creator
        self._saju_hash_resolver = saju_hash_resolver
        self._analytics = analytics
        self._user_demographics = user_demographics

    async def execute(self, form: dict[str, Any]) -> FeedbackResult:
        # 1. 인증 검증
        if form.get("linkkey") != self._expected_linkkey:
            logger.warning("PayApp feedback linkkey mismatch")
            return FeedbackResult(ok=False, reason="linkkey_mismatch")
        if form.get("linkval") != self._expected_linkval:
            logger.warning("PayApp feedback linkval mismatch")
            return FeedbackResult(ok=False, reason="linkval_mismatch")

        order_id = form.get("var1")
        mul_no = form.get("mul_no")
        pay_state = form.get("pay_state")
        price_str = form.get("price")

        if not order_id or not pay_state:
            logger.warning(
                "PayApp feedback missing required fields (order_id=%s, pay_state=%s)",
                order_id,
                pay_state,
            )
            return FeedbackResult(ok=False, reason="missing_fields")

        # 2. payment 조회 + 금액 검증
        payment = await self._repo.find_by_order_id(order_id)
        if payment is None:
            logger.warning("PayApp feedback unknown order_id=%s", order_id)
            return FeedbackResult(ok=False, reason="unknown_order")

        # PayApp price는 string. payment.amount는 int. 비교 위해 변환.
        try:
            received_amount = int(str(price_str))
        except (ValueError, TypeError):
            logger.warning("PayApp feedback invalid price=%s", price_str)
            return FeedbackResult(ok=False, reason="invalid_price")
        if received_amount != payment.amount:
            logger.warning(
                "PayApp feedback amount mismatch: db=%s, payapp=%s",
                payment.amount,
                received_amount,
            )
            return FeedbackResult(ok=False, reason="amount_mismatch")

        # 3. pay_state 매핑
        new_status = _PAY_STATE_TO_STATUS.get(str(pay_state))
        if new_status is None:
            logger.warning("PayApp feedback unknown pay_state=%s", pay_state)
            # 알 수 없는 상태도 SUCCESS 응답 — 재시도 방지
            return FeedbackResult(ok=True, reason="unknown_pay_state_ignored")

        # 4. 멱등성 — 이미 같은 상태면 skip (PayApp가 재시도해도 안전)
        if payment.status == new_status:
            return FeedbackResult(ok=True, reason="duplicate_skipped")

        # 5. 상태 갱신
        approved_at: datetime | None = None
        if new_status == PaymentStatus.DONE:
            approved_at = _parse_pay_date(form.get("pay_date")) or datetime.now(UTC)
        updated = await self._repo.update_status(
            order_id=order_id,
            status=new_status,
            approved_at=approved_at,
        )
        if updated is None:
            return FeedbackResult(ok=False, reason="update_failed")

        # 6. 결제완료 시 후속 처리 (AI 합성 + Amplitude)
        if new_status == PaymentStatus.DONE:
            await self._trigger_post_payment(updated, mul_no=str(mul_no or ""))

        return FeedbackResult(ok=True, reason=f"status_{new_status.value}")

    async def _trigger_post_payment(self, payment: Any, *, mul_no: str) -> None:
        # PaidReport 합성 트리거
        if self._paid_report_creator is not None:
            saju_hash: str | None = None
            if self._saju_hash_resolver is not None:
                saju_hash = await self._saju_hash_resolver.resolve(payment.user_id)
            try:
                await self._paid_report_creator.execute(
                    order_id=payment.order_id,
                    saju_hash=saju_hash or payment.order_id,
                    user_id=payment.user_id,
                    customer_email=payment.customer_email,
                    expires_at=payment.expires_at,
                    character=payment.character.value,
                )
            except Exception as e:  # noqa: BLE001
                logger.warning("paid_report_creator failed: %s", e)

        # Amplitude 트래킹 (fire-and-forget). PayApp 플로엔 device_id/session_id 없음 → None.
        if self._analytics is not None:
            gender: str | None = None
            if self._user_demographics is not None:
                try:
                    gender = await self._user_demographics.find_gender_by_user_id(
                        payment.user_id
                    )
                except Exception as e:  # noqa: BLE001
                    logger.warning("user_demographics failed: %s", e)
            asyncio.create_task(
                safe_track_payment_completed(
                    analytics=self._analytics,
                    user_id=payment.user_id,
                    device_id=None,
                    session_id=None,
                    order_id=payment.order_id,
                    character=payment.character.value,
                    amount=payment.amount,
                    method=None,
                    easy_pay_provider=None,
                    card_issuer_code=None,
                    bank_code=None,
                    approved_at=payment.approved_at,
                    gender=gender,
                )
            )


def _parse_pay_date(value: Any) -> datetime | None:
    """PayApp pay_date 형식: 'YYYY-MM-DD HH:MM:SS' (KST). UTC로 변환해서 저장."""
    if not isinstance(value, str) or not value:
        return None
    try:
        # 단순 파싱 (timezone 없음 → naive). KST 가정 후 UTC 변환은 운영 정책에 따라 추후.
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    except ValueError:
        return None
