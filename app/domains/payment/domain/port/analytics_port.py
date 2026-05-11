"""결제 도메인에서 분석 시스템(Amplitude 등)으로 이벤트를 보내는 Port.

Hexagonal 룰: payment 도메인은 Amplitude SDK / httpx 를 직접 import 하지 않는다.
main.py가 인프라 어댑터를 주입한다.

호출 측은 fire-and-forget 으로 부르므로, 구현체는 예외를 던지지 않는다.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class AnalyticsPort(Protocol):
    async def track_payment_completed(
        self,
        *,
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
    ) -> None: ...
