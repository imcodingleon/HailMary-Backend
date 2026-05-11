"""AnalyticsPort 의 Amplitude 구현체.

payment 도메인의 결제 완료 신호를 Amplitude HTTP API V2 페이로드로 변환해 전송한다.

PII 정책 (절대 변경 금지):
- event_properties 는 화이트리스트 키만 허용.
- customer_email / 이름 / 전화번호 / 생년월일은 절대 포함 금지.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.domains.payment.domain.port.analytics_port import AnalyticsPort
from app.infrastructure.external.amplitude.client import AmplitudeClient


class AmplitudeAnalyticsAdapter(AnalyticsPort):
    def __init__(self, *, client: AmplitudeClient, environment: str) -> None:
        self._client = client
        self._environment = environment

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
    ) -> None:
        event: dict[str, Any] = {
            "event_type": "payment_completed",
            "user_id": f"user_{user_id}",
            "event_properties": {
                "character_id": character,
                "order_id": order_id,
                "amount": amount,
                "payment_method": method,
                "easy_pay_provider": easy_pay_provider,
                "card_issuer_code": card_issuer_code,
                "bank_code": bank_code,
                "paid_at": approved_at.isoformat(),
                "environment": self._environment,
            },
            "time": int(approved_at.timestamp() * 1000),
            "insert_id": f"payment_completed-{order_id}",
        }
        if device_id:
            event["device_id"] = device_id
        if session_id is not None:
            event["session_id"] = session_id

        await self._client.send_event(event)
