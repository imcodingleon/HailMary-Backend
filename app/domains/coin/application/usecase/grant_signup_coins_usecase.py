"""가입 지급 usecase (Task 5).

신규 계정에 FREE 코인을 1회 지급한다. `CoinLot.ref = "signup:{account_id}"` 에
UNIQUE(source_reason, ref) 제약이 걸려 있어 중복 지급 시도는 DB(또는 인메모리 페이크)
레벨에서 거부되며, 이 usecase는 그 거부를 삼켜 멱등하게 동작한다 —
재로그인/재시도로 두 번 호출되어도 지급은 한 번만 이뤄진다.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from app.domains.coin.application.coin_ports import CoinLedgerPort
from app.domains.coin.domain.entity.coin_models import CoinLot
from app.domains.coin.domain.value_object.coin_enums import CoinType, SourceReason


class GrantSignupCoinsUseCase:
    def __init__(
        self,
        *,
        ledger: CoinLedgerPort,
        grant_amount: int,
        expiry_days: int | None,
        now_fn: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._ledger = ledger
        self._amount = grant_amount
        self._expiry_days = expiry_days
        self._now = now_fn

    async def grant(self, account_id: int) -> None:
        now = self._now()
        expires_at = (
            None if self._expiry_days is None else now + timedelta(days=self._expiry_days)
        )
        lot = CoinLot(
            account_id=account_id,
            coin_type=CoinType.FREE,
            source_reason=SourceReason.SIGNUP_GRANT,
            original_amount=self._amount,
            remaining_amount=self._amount,
            ref=f"signup:{account_id}",
            acquired_at=now,
            expires_at=expires_at,
            status="ACTIVE",
        )
        try:
            await self._ledger.create_wallet_with_lot(lot)
        except Exception as exc:  # noqa: BLE001 — 중복 지급 감지 후 재-raise
            if _is_duplicate(exc):
                return  # 이미 지급됨 — 멱등 무시
            raise


def _is_duplicate(exc: Exception) -> bool:
    # FakeLedger는 ValueError("duplicate lot ref"), 실 DB는 IntegrityError.
    from sqlalchemy.exc import IntegrityError

    return isinstance(exc, IntegrityError) or "duplicate" in str(exc).lower()
