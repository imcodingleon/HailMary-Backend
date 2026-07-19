"""만료된 coin lot 배치 sweep 엔트리포인트.

수동/크론 실행용 얇은 진입점. GetBalance는 조회 시점 lazy 만료만 처리하므로,
조회되지 않는 계정의 만료 lot은 이 배치가 없으면 영영 EXPIRED로 전환되지 않는다.

실행: python -X utf8 -m scripts.coin.sweep_expired
"""
from __future__ import annotations

import asyncio
import sys

from app.domains.coin.adapter.outbound.persistence.coin_repository import (
    CoinRepository,
)
from app.domains.coin.application.usecase.sweep_expired_lots_usecase import (
    SweepExpiredLotsUseCase,
)
from app.infrastructure.database.session import AsyncSessionLocal


async def main() -> None:
    async with AsyncSessionLocal() as session:
        ledger = CoinRepository(session)
        usecase = SweepExpiredLotsUseCase(ledger=ledger)
        swept = await usecase.run()
        await session.commit()

    print(f"[sweep] 만료 처리한 account 수: {swept}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
