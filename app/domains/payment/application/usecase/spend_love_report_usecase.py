"""연애운 코인 해금 UseCase (도화선 2.0 P4 Unit B, 로그인 계정 전용).

유효한 세션 + 코인 잔액(490)을 원자적으로 소진하고 amount=0 결제(DONE)를 생성해
PayApp 을 완전히 우회하면서 유료 결과지 합성을 트리거한다. 무료 쿠폰 리뎀션
(`RedeemCouponUseCase`)과 동일 골격이되, 소진 대상이 쿠폰 코드 대신 코인 잔액.

결과지 합성은 쿠폰과 동일하게 **백그라운드**(`background_composer`)로 돌려 응답을
막지 않는다 — 도윤 결과지의 긴 AI 합성 대기를 버튼에서 떼어내 결과 로딩 화면이 흡수하게 한다.

로그인 필수: account_id 는 필수 인자다. 라우터가 미로그인 요청을 401 로 거부한 뒤에만
이 UseCase 에 진입한다(이 UseCase 자체는 인증을 검증하지 않는다).
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable, Coroutine
from typing import Any

from app.domains.payment.application.payment_ports import (
    CoinSpendPort,
    UserDemographicsPort,
    UserLookupPort,
)
from app.domains.payment.application.usecase._grant_paid_report import (
    grant_paid_report,
)
from app.domains.payment.domain.port.analytics_port import AnalyticsPort
from app.domains.payment.domain.port.payment_repository_port import (
    PaymentRepositoryPort,
)
from app.domains.payment.domain.value_object.payment_status import CharacterCode
from app.infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)


class SpendLoveReportUseCase:
    def __init__(
        self,
        *,
        coin_spend: CoinSpendPort,
        repo: PaymentRepositoryPort,
        user_lookup: UserLookupPort,
        background_composer: Callable[..., Coroutine[Any, Any, None]] | None = None,
        analytics: AnalyticsPort | None = None,
        user_demographics: UserDemographicsPort | None = None,
    ) -> None:
        self._coin_spend = coin_spend
        self._repo = repo
        self._user_lookup = user_lookup
        self._background_composer = background_composer
        self._analytics = analytics
        self._user_demographics = user_demographics

    async def execute(
        self,
        *,
        session_token: str,
        character: CharacterCode,
        customer_email: str,
        account_id: int,
        device_id: str | None = None,
        session_id: int | None = None,
    ) -> str:
        """코인 소진 + 무료 결과지 발급. 응답: orderId.

        순서가 핵심: user 확인 → 코인 소진(부족 시 InsufficientCoinsError 전파,
        라우터가 402 로 매핑) → 발급. 소진을 발급보다 먼저 잡아 잔액 부족 시
        결제/합성이 생성되지 않도록 한다. 환불 사가는 범위 밖(P5) — 소진 성공 후
        발급 단계 실패는 이 태스크에서 다루지 않는다.
        """
        user_id = await self._user_lookup.find_user_id_by_session_token(session_token)
        if user_id is None:
            raise ValueError("세션이 만료되었거나 잘못된 토큰입니다.")

        order_id = f"coin_{uuid.uuid4().hex}"
        cost = get_settings().love_report_coin_cost

        new_balance = await self._coin_spend.spend(account_id, cost=cost, ref=order_id)

        logger.warning(
            "[COIN] spent cost=%s balance=%s user=%s order=%s",
            cost,
            new_balance,
            user_id,
            order_id,
        )

        saved = await grant_paid_report(
            repo=self._repo,
            user_id=user_id,
            character=character,
            customer_email=customer_email,
            amount=0,  # KRW 미발생 — 코인 소진은 charge 시점에 인식(이중 계산 방지)
            order_id=order_id,
            payment_key=f"coin-{order_id}",
            paid_report_creator=None,
            saju_hash_resolver=None,
            analytics=self._analytics,
            user_demographics=self._user_demographics,
            log_tag="COIN",
            method="coin",  # 코인 소진 결제 — 분석 구분용
            background_composer=self._background_composer,  # 합성은 백그라운드(응답 비대기)
            account_id=account_id,  # 로그인 필수 — 보관함 귀속
            device_id=device_id,  # Amplitude FE 유저 연결
            session_id=session_id,
        )
        return saved.order_id
