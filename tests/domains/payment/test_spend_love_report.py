"""SpendLoveReportUseCase 핵심 분기 단위 테스트.

RedeemCouponUseCase(쿠폰 리뎀션)와 동일 골격 — 소진 대상만 쿠폰 코드 대신 코인 잔액으로
바뀐다. 결제(PayApp)를 완전히 우회하고 amount=0 결제(DONE)를 생성해 무료 쿠폰 플로와
동일하게 결과지 합성을 트리거한다.

대상:
    1. happy path — 코인 소진(cost=490, ref=order_id) 후 amount=0 Payment(DONE) 생성,
       method="coin" 으로 분석 발화, 합성 백그라운드 스폰.
    2. 잔액 부족 — InsufficientCoinsError 전파(라우터가 402로 매핑), 결제/합성 생성 안 됨.
    3. 세션 만료 — ValueError, 코인 소진 시도 자체 없음.

Mock 전략: unittest.mock 대신 Port 직접 구현 fake.
"""

import asyncio
from collections.abc import Coroutine
from datetime import datetime
from typing import Any

import pytest

from app.domains.coin.domain.error import InsufficientCoinsError
from app.domains.payment.application.payment_ports import CoinSpendPort
from app.domains.payment.application.usecase.spend_love_report_usecase import (
    SpendLoveReportUseCase,
)
from app.domains.payment.domain.entity.payment import Payment
from app.domains.payment.domain.port.analytics_port import AnalyticsPort
from app.domains.payment.domain.port.payment_repository_port import (
    PaymentRepositoryPort,
)
from app.domains.payment.domain.value_object.payment_status import (
    CharacterCode,
    PaymentStatus,
)

# ── Test fakes ────────────────────────────────────────────────────────────────


class FakeCoinSpendPort(CoinSpendPort):
    """In-memory 코인 지갑. 잔액 이하 소진만 성공, 초과 시 InsufficientCoinsError."""

    def __init__(self, balance: int = 1000) -> None:
        self.balance = balance
        self.spend_calls: list[tuple[int, int, str]] = []

    async def spend(self, account_id: int, cost: int, ref: str) -> int:
        self.spend_calls.append((account_id, cost, ref))
        if cost > self.balance:
            raise InsufficientCoinsError(available=self.balance, required=cost)
        self.balance -= cost
        return self.balance


class FakePaymentRepository(PaymentRepositoryPort):
    def __init__(self) -> None:
        self._by_order_id: dict[str, Payment] = {}
        self.save_calls: list[Payment] = []

    async def save(self, payment: Payment) -> Payment:
        self.save_calls.append(payment)
        saved = Payment(
            payment_key=payment.payment_key,
            order_id=payment.order_id,
            user_id=payment.user_id,
            character=payment.character,
            amount=payment.amount,
            status=payment.status,
            customer_email=payment.customer_email,
            approved_at=payment.approved_at,
            expires_at=payment.expires_at,
            account_id=payment.account_id,
            id=payment.id or len(self._by_order_id) + 1,
        )
        self._by_order_id[payment.order_id] = saved
        return saved

    async def find_by_order_id(self, order_id: str) -> Payment | None:
        return self._by_order_id.get(order_id)

    async def find_by_payment_key(self, payment_key: str) -> Payment | None:
        for p in self._by_order_id.values():
            if p.payment_key == payment_key:
                return p
        return None

    async def update_status(
        self, *, order_id: str, status: PaymentStatus, approved_at: datetime | None = None
    ) -> Payment | None:
        return self._by_order_id.get(order_id)

    async def update_customer_email(
        self, *, order_id: str, new_email: str
    ) -> Payment | None:
        return self._by_order_id.get(order_id)

    async def confirm_email(
        self, *, order_id: str, email: str
    ) -> tuple[Payment, bool] | None:
        p = self._by_order_id.get(order_id)
        if p is None:
            return None
        changed = p.customer_email != email
        return p, changed

    async def mark_result_email_sent(self, *, order_id: str) -> None:
        return None

    async def find_email_unsent_done(
        self, *, unconfirmed_grace_seconds: int, limit: int = 20
    ) -> list[Payment]:
        return []


class FakeUserLookup:
    def __init__(self, mapping: dict[str, int] | None = None) -> None:
        self._mapping = mapping if mapping is not None else {"VALID-TOKEN": 42}

    async def find_user_id_by_session_token(self, token: str) -> int | None:
        return self._mapping.get(token)


class FakeBackgroundComposer:
    """백그라운드 합성 callable fake. 스폰 시점에 calls 기록, tick 후 ran=True."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.ran = False

    def __call__(self, **kwargs: Any) -> Coroutine[Any, Any, None]:
        self.calls.append(kwargs)

        async def _run() -> None:
            self.ran = True

        return _run()


class FakeAnalytics(AnalyticsPort):
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def track_payment_completed(self, **kwargs: Any) -> None:
        self.calls.append(kwargs)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _usecase(
    *,
    coin_spend: FakeCoinSpendPort,
    repo: FakePaymentRepository,
    user_lookup: FakeUserLookup | None = None,
    background_composer: FakeBackgroundComposer | None = None,
    analytics: FakeAnalytics | None = None,
) -> SpendLoveReportUseCase:
    return SpendLoveReportUseCase(
        coin_spend=coin_spend,
        repo=repo,
        user_lookup=user_lookup or FakeUserLookup(),
        background_composer=background_composer,
        analytics=analytics,
        user_demographics=None,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


async def test_happy_path_spends_coin_and_creates_free_payment() -> None:
    coin_spend = FakeCoinSpendPort(balance=1000)
    repo = FakePaymentRepository()
    composer = FakeBackgroundComposer()
    analytics = FakeAnalytics()
    usecase = _usecase(
        coin_spend=coin_spend, repo=repo, background_composer=composer, analytics=analytics
    )

    order_id = await usecase.execute(
        session_token="VALID-TOKEN",
        character=CharacterCode.YEONWOO,
        customer_email="buyer@example.com",
        account_id=7,
    )

    assert order_id.startswith("coin_")

    # 코인 소진: cost=490(settings.love_report_coin_cost), ref=order_id
    assert len(coin_spend.spend_calls) == 1
    spent_account_id, spent_cost, spent_ref = coin_spend.spend_calls[0]
    assert spent_account_id == 7
    assert spent_cost == 490
    assert spent_ref == order_id
    assert coin_spend.balance == 1000 - 490

    # 결제: amount=0 (KRW 미발생 — 코인 소진은 charge 시점에 인식)
    assert len(repo.save_calls) == 1
    saved = repo.save_calls[0]
    assert saved.amount == 0
    assert saved.status == PaymentStatus.DONE
    assert saved.order_id == order_id
    assert saved.account_id == 7

    # 합성은 스폰되었지만 아직 실행 전 (= execute 는 합성 완료를 기다리지 않는다)
    assert len(composer.calls) == 1
    assert composer.ran is False
    assert composer.calls[0]["order_id"] == order_id
    assert composer.calls[0]["character"] == "yeonwoo"

    await asyncio.sleep(0)
    assert composer.ran is True

    # 분석: method="coin", amount=0
    assert len(analytics.calls) == 1
    assert analytics.calls[0]["method"] == "coin"
    assert analytics.calls[0]["amount"] == 0
    assert "customer_email" not in analytics.calls[0], "PII 금지"


async def test_insufficient_coins_propagates() -> None:
    coin_spend = FakeCoinSpendPort(balance=100)  # 490 미만
    repo = FakePaymentRepository()
    composer = FakeBackgroundComposer()
    usecase = _usecase(coin_spend=coin_spend, repo=repo, background_composer=composer)

    with pytest.raises(InsufficientCoinsError):
        await usecase.execute(
            session_token="VALID-TOKEN",
            character=CharacterCode.YEONWOO,
            customer_email="buyer@example.com",
            account_id=7,
        )

    assert len(coin_spend.spend_calls) == 1, "소진 시도는 했으나 실패"
    assert repo.save_calls == [], "잔액 부족이면 결제 생성 금지"
    assert composer.calls == [], "잔액 부족이면 합성 스폰 금지"


async def test_expired_session_does_not_attempt_spend() -> None:
    coin_spend = FakeCoinSpendPort(balance=1000)
    repo = FakePaymentRepository()
    composer = FakeBackgroundComposer()
    usecase = _usecase(
        coin_spend=coin_spend,
        repo=repo,
        user_lookup=FakeUserLookup({}),  # 토큰 매핑 없음
        background_composer=composer,
    )

    with pytest.raises(ValueError):
        await usecase.execute(
            session_token="EXPIRED",
            character=CharacterCode.YEONWOO,
            customer_email="buyer@example.com",
            account_id=7,
        )

    assert coin_spend.spend_calls == [], "세션 무효면 코인 소진 시도 자체 없음"
    assert repo.save_calls == []
    assert composer.calls == []
