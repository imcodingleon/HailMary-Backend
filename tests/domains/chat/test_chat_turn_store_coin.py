"""ChatTurnStore 코인 선차감 배선 — 원자성(같은 트랜잭션) 검증 (P4-step-1, money-critical).

실제 SQLite in-memory 엔진 + async session factory로 begin_turn()의
``session.begin()`` 트랜잭션 경계 안에서 코인 차감이 이뤄지는지, 부족 시
user 메시지 INSERT까지 롤백되는지를 검증한다. FakeChatCoinSpendPort로
coin 도메인 실제 원장 없이 ChatCoinSpendPort 계약만 흉내 낸다 — 롤백 검증에
필요한 건 "코인 스텝이 user INSERT와 같은 트랜잭션에 있다"는 사실뿐이라
coin_lots/coin_wallets 테이블은 불필요.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domains.auth.infrastructure.orm.account_orm import AccountORM
from app.domains.chat.adapter.outbound.persistence.chat_turn_store import ChatTurnStore
from app.domains.chat.domain.value_object.chat_enums import ChatCharacter, ChatMode
from app.domains.chat.infrastructure.orm.chat_message_orm import ChatMessageORM
from app.domains.chat.infrastructure.orm.conversation_orm import ConversationORM
from app.domains.chat.infrastructure.orm.saju_profile_orm import SajuProfileORM
from app.domains.coin.domain.error import InsufficientCoinsError
from app.infrastructure.database.session import Base

PERSONAL_COST = 1
SAJU_COST = 5


class FakeChatCoinSpendPort:
    """ChatCoinSpendPort 흉내 — spend 호출 기록, insufficient=True면 예외."""

    def __init__(self, *, insufficient: bool = False, new_balance: int = 99) -> None:
        self.insufficient = insufficient
        self.new_balance = new_balance
        self.calls: list[tuple[int, int, str]] = []

    async def spend(self, account_id: int, cost: int, ref: str) -> int:
        self.calls.append((account_id, cost, ref))
        if self.insufficient:
            raise InsufficientCoinsError(available=0, required=cost)
        return self.new_balance


@pytest.fixture
async def session_factory() -> AsyncGenerator[Callable[[], AsyncSession], None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all,
            tables=[
                AccountORM.__table__,
                ConversationORM.__table__,
                ChatMessageORM.__table__,
                SajuProfileORM.__table__,
            ],
        )
    maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield maker
    finally:
        await engine.dispose()


@pytest.fixture
async def conversation_id(session_factory: Callable[[], AsyncSession]) -> int:
    async with session_factory() as session, session.begin():
        conv = ConversationORM(account_id=1, character_id=ChatCharacter.YEONU.value)
        session.add(conv)
        await session.flush()
        return conv.id


async def _message_count(
    session_factory: Callable[[], AsyncSession], conversation_id: int
) -> int:
    async with session_factory() as session:
        rows = (
            await session.execute(
                select(ChatMessageORM).where(
                    ChatMessageORM.conversation_id == conversation_id
                )
            )
        ).scalars().all()
        return len(rows)


async def test_casual_turn_spends_personal_cost_with_turn_ref(
    session_factory: Callable[[], AsyncSession], conversation_id: int
) -> None:
    fake_port = FakeChatCoinSpendPort(new_balance=99)
    store = ChatTurnStore(
        session_factory,
        personal_cost=PERSONAL_COST,
        saju_cost=SAJU_COST,
        coin_spend_factory=lambda session: fake_port,
    )

    begin = await store.begin_turn(
        conversation_id=conversation_id,
        account_id=1,
        content="안녕",
        mode=ChatMode.CASUAL,
        history_window=20,
    )

    assert begin.cost == PERSONAL_COST
    assert begin.balance == 99
    assert fake_port.calls == [(1, PERSONAL_COST, f"chat_turn:{begin.user_message_id}")]


async def test_saju_turn_spends_saju_cost(
    session_factory: Callable[[], AsyncSession], conversation_id: int
) -> None:
    fake_port = FakeChatCoinSpendPort(new_balance=42)
    store = ChatTurnStore(
        session_factory,
        personal_cost=PERSONAL_COST,
        saju_cost=SAJU_COST,
        coin_spend_factory=lambda session: fake_port,
    )

    begin = await store.begin_turn(
        conversation_id=conversation_id,
        account_id=1,
        content="사주 봐줘",
        mode=ChatMode.SAJU,
        history_window=20,
    )

    assert begin.cost == SAJU_COST
    assert begin.balance == 42
    assert fake_port.calls == [(1, SAJU_COST, f"chat_turn:{begin.user_message_id}")]


async def test_insufficient_coins_rolls_back_user_message(
    session_factory: Callable[[], AsyncSession], conversation_id: int
) -> None:
    """money-critical 핵심 보증: 코인 부족 시 user 메시지 INSERT도 함께 롤백돼야
    유령(orphan) 메시지가 남지 않는다."""
    fake_port = FakeChatCoinSpendPort(insufficient=True)
    store = ChatTurnStore(
        session_factory,
        personal_cost=PERSONAL_COST,
        saju_cost=SAJU_COST,
        coin_spend_factory=lambda session: fake_port,
    )

    with pytest.raises(InsufficientCoinsError):
        await store.begin_turn(
            conversation_id=conversation_id,
            account_id=1,
            content="안녕",
            mode=ChatMode.CASUAL,
            history_window=20,
        )

    assert await _message_count(session_factory, conversation_id) == 0
    assert fake_port.calls  # spend는 시도됐다 (call 자체는 남음, DB row만 롤백)


async def test_factory_none_skips_spend_and_still_persists_message(
    session_factory: Callable[[], AsyncSession], conversation_id: int
) -> None:
    """coin_enabled=False → main.py가 factory=None 주입 → 채팅은 무료."""
    store = ChatTurnStore(
        session_factory,
        personal_cost=PERSONAL_COST,
        saju_cost=SAJU_COST,
        coin_spend_factory=None,
    )

    begin = await store.begin_turn(
        conversation_id=conversation_id,
        account_id=1,
        content="안녕",
        mode=ChatMode.CASUAL,
        history_window=20,
    )

    assert begin.cost == 0
    assert begin.balance is None
    assert await _message_count(session_factory, conversation_id) == 1
