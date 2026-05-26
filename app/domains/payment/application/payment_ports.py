"""결제 후처리(웹훅/AI 합성/분석) 공용 Port 정의.

PayApp feedback UseCase가 사용하는 외부 의존성 Port들 — payment 도메인이 user/ai
도메인을 직접 import하지 않도록 추상화. main.py가 어댑터 주입.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Protocol

from app.domains.payment.domain.port.analytics_port import AnalyticsPort

logger = logging.getLogger(__name__)


class PaidReportCreatorPort(Protocol):
    """결제 완료 직후 호출되는 PaidReport 생성 hook.

    AI 도메인 의존성 역전: payment 도메인은 ai 도메인을 import하지 않는다.
    main.py에서 CreatePaidReportUseCase를 어댑터로 주입한다.
    """

    async def execute(
        self,
        *,
        order_id: str,
        saju_hash: str,
        user_id: int | None = None,
        customer_email: str | None = None,
        expires_at: datetime | None = None,
        character: str | None = None,
    ) -> object: ...


class SajuHashResolverPort(Protocol):
    """user_id로 사주 해시를 계산해 돌려주는 hook."""

    async def resolve(self, user_id: int) -> str | None: ...


class UserLookupPort(Protocol):
    """sessionToken으로 user_id를 조회하는 hook."""

    async def find_user_id_by_session_token(self, token: str) -> int | None: ...


class UserDemographicsPort(Protocol):
    """user_id로 분석용 인구통계(현재는 gender)를 조회하는 hook."""

    async def find_gender_by_user_id(self, user_id: int) -> str | None: ...


async def safe_track_payment_completed(
    *,
    analytics: AnalyticsPort,
    user_id: int,
    device_id: str | None,
    session_id: int | None,
    order_id: str,
    character: str,
    amount: int,
    method: str | None,
    easy_pay_provider: str | None,
    card_issuer_code: str | None,
    bank_code: str | None,
    approved_at: datetime,
    gender: str | None,
) -> None:
    """analytics.track_payment_completed 의 모든 예외를 swallow.

    asyncio.create_task로 fire-and-forget 호출 시 unhandled exception 방지용 래퍼.
    """
    try:
        await analytics.track_payment_completed(
            user_id=user_id,
            device_id=device_id,
            session_id=session_id,
            order_id=order_id,
            character=character,
            amount=amount,
            method=method,
            easy_pay_provider=easy_pay_provider,
            card_issuer_code=card_issuer_code,
            bank_code=bank_code,
            approved_at=approved_at,
            gender=gender,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("analytics.track_payment_completed failed: %s", e)
