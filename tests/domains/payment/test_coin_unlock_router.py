"""coin_unlock_router HTTP 계약 테스트 (도화선 2.0 P4 Unit B).

대상: POST /api/coins/spend/love-report
    1. 로그인 없음 → 401 (get_current_account_id 가드, usecase 미호출)
    2. 정상 → 201 + {"orderId": ...}
    3. 잔액 부족(InsufficientCoinsError) → 402

UseCase는 fake로 대체 — HTTP 계층(인증 가드 + 상태코드 매핑)만 검증한다.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domains.auth.adapter.inbound.api.auth_router import (
    get_current_account_id,
    get_token_issuer,
)
from app.domains.coin.domain.error import InsufficientCoinsError
from app.domains.payment.adapter.inbound.api.coin_unlock_router import (
    get_spend_love_report_usecase,
    router,
)
from app.domains.payment.domain.value_object.payment_status import CharacterCode

_BODY = {
    "sessionToken": "VALID-TOKEN",
    "character": CharacterCode.YEONWOO.value,
    "customerEmail": "buyer@example.com",
}


class FakeSpendLoveReportUseCase:
    def __init__(self, *, order_id: str | None = None, error: Exception | None = None) -> None:
        self._order_id = order_id
        self._error = error
        self.calls: list[dict[str, Any]] = []

    async def execute(self, **kwargs: Any) -> str:
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        assert self._order_id is not None
        return self._order_id


def _make_app(*, usecase: FakeSpendLoveReportUseCase, account_id: int | None = 7) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_spend_love_report_usecase] = lambda: usecase
    if account_id is not None:
        app.dependency_overrides[get_current_account_id] = lambda: account_id
    return app


def test_no_auth_returns_401() -> None:
    usecase = FakeSpendLoveReportUseCase(order_id="coin_abc")
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_spend_love_report_usecase] = lambda: usecase
    # get_current_account_id 자체는 오버라이드하지 않음 — 실제 401 가드 경로 그대로 태운다.
    # 단, FastAPI는 하위 의존성(get_token_issuer)을 함수 본문 실행 전에 미리 해석하므로
    # (헤더 누락 분기가 그걸 쓰지 않아도) 더미로 채워야 NotImplementedError를 피한다.
    app.dependency_overrides[get_token_issuer] = lambda: object()
    client = TestClient(app)

    resp = client.post("/api/coins/spend/love-report", json=_BODY)

    assert resp.status_code == 401
    assert usecase.calls == [], "인증 실패면 usecase 자체를 호출하면 안 된다"


def test_success_returns_201_with_order_id() -> None:
    usecase = FakeSpendLoveReportUseCase(order_id="coin_abc123")
    app = _make_app(usecase=usecase, account_id=7)
    client = TestClient(app)

    resp = client.post("/api/coins/spend/love-report", json=_BODY)

    assert resp.status_code == 201
    assert resp.json() == {"orderId": "coin_abc123"}
    assert len(usecase.calls) == 1
    call = usecase.calls[0]
    assert call["account_id"] == 7
    assert call["session_token"] == "VALID-TOKEN"
    assert call["customer_email"] == "buyer@example.com"


def test_insufficient_coins_returns_402() -> None:
    error = InsufficientCoinsError(available=100, required=490)
    usecase = FakeSpendLoveReportUseCase(error=error)
    app = _make_app(usecase=usecase, account_id=7)
    client = TestClient(app)

    resp = client.post("/api/coins/spend/love-report", json=_BODY)

    assert resp.status_code == 402
