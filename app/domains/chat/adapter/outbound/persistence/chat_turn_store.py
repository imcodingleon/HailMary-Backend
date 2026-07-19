from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.chat.domain.entity.chat_message import ChatMessage
from app.domains.chat.domain.port.chat_coin_spend_port import ChatCoinSpendPort
from app.domains.chat.domain.port.chat_turn_store_port import TurnBegin
from app.domains.chat.domain.port.conversation_repository_port import (
    ConversationNotFoundError,
)
from app.domains.chat.domain.value_object.chat_enums import ChatCharacter, ChatMode
from app.domains.chat.infrastructure.mapper.chat_mapper import ChatMessageMapper
from app.domains.chat.infrastructure.orm.chat_message_orm import ChatMessageORM
from app.domains.chat.infrastructure.orm.conversation_orm import ConversationORM
from app.domains.chat.infrastructure.orm.saju_profile_orm import SajuProfileORM


class ChatTurnStore:
    """스트리밍 턴 영속화 (ChatTurnStorePort 구현) — 단명 자체 세션.

    요청 세션(`_get_session`, 요청당 단일 트랜잭션)을 스트림 수명 동안 잡지 않기 위해
    각 메서드가 session_factory로 자체 세션을 열고 원자 커밋한다
    (main.py `_compose_report_background` 패턴, CHAT_SSOT.md SSE 계약 §코인 선차감-환불).

    코인 선차감(P4-step-1): coin_spend_factory가 주어지면(coin_enabled=True) user
    메시지 INSERT와 **같은** session.begin() 블록 안에서 코인을 소진한다 — 부족 시
    InsufficientCoinsError가 전파되며 해당 트랜잭션(방금 flush한 user 메시지 포함)이
    통째로 롤백돼 유령(orphan) 메시지가 남지 않는다. factory=None(coin_enabled=False)
    이면 소진 자체를 건너뛰어 채팅이 무료로 동작한다.
    """

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        *,
        personal_cost: int = 0,
        saju_cost: int = 0,
        coin_spend_factory: Callable[[AsyncSession], ChatCoinSpendPort] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._personal_cost = personal_cost
        self._saju_cost = saju_cost
        self._coin_spend_factory = coin_spend_factory

    async def begin_turn(
        self,
        *,
        conversation_id: int,
        account_id: int,
        content: str,
        mode: ChatMode,
        history_window: int,
    ) -> TurnBegin:
        async with self._session_factory() as session, session.begin():
            conv = (
                await session.execute(
                    select(ConversationORM).where(
                        ConversationORM.id == conversation_id,
                        ConversationORM.account_id == account_id,
                    )
                )
            ).scalar_one_or_none()
            if conv is None:
                raise ConversationNotFoundError(f"conversation {conversation_id} not found")

            # 직전 이력 (user 메시지 INSERT 전 스냅샷, 최신 N → 오름차순)
            rows = (
                (
                    await session.execute(
                        select(ChatMessageORM)
                        .where(ChatMessageORM.conversation_id == conversation_id)
                        .order_by(ChatMessageORM.id.desc())
                        .limit(history_window)
                    )
                )
                .scalars()
                .all()
            )
            history: list[ChatMessage] = [ChatMessageMapper.to_entity(r) for r in reversed(rows)]

            user_orm = ChatMessageORM(
                conversation_id=conversation_id,
                role="user",
                msg_type="text",
                mode=mode.value,
                content=content,
            )
            session.add(user_orm)
            conv.last_message_at = datetime.now()
            await session.flush()  # user_orm.id 확보 (아래 코인 ref에 필요)

            # 코인 선차감 — user INSERT와 같은 트랜잭션. 부족 시 예외가 여기서 던져지고
            # session.begin()이 통째로 롤백(위 INSERT도 함께 취소)한다.
            # ref는 user_message_id 기준 — 빠른 연타 더블클릭은 메시지 2개=차감 2회로
            # 별도 턴 취급한다(연애운 Unit B와 동일 클래스의 더블서브밋, P5 검토 항목).
            cost = 0
            balance: int | None = None
            if self._coin_spend_factory is not None:
                cost = self._personal_cost if mode == ChatMode.CASUAL else self._saju_cost
                coin_spend = self._coin_spend_factory(session)
                balance = await coin_spend.spend(
                    account_id, cost, ref=f"chat_turn:{user_orm.id}"
                )

            # 계정 사주 프로필(있으면) 동승 — 프롬프트 컨텍스트 주입용 (H2/H3)
            saju_raw = (
                await session.execute(
                    select(SajuProfileORM.saju_raw).where(
                        SajuProfileORM.account_id == account_id
                    )
                )
            ).scalar_one_or_none()

            return TurnBegin(
                character=ChatCharacter(conv.character_id),
                user_message_id=user_orm.id,
                history=history,
                saju_raw=saju_raw,
                cost=cost,
                balance=balance,
            )

    async def complete_turn(
        self,
        *,
        conversation_id: int,
        content: str,
        mode: ChatMode,
        msg_type: str = "text",
        saju_block: dict[str, Any] | None = None,
    ) -> int:
        async with self._session_factory() as session, session.begin():
            orm = ChatMessageORM(
                conversation_id=conversation_id,
                role="character",
                msg_type=msg_type,
                mode=mode.value,
                content=content,
                saju_block=saju_block,
            )
            session.add(orm)
            conv = (
                await session.execute(
                    select(ConversationORM).where(ConversationORM.id == conversation_id)
                )
            ).scalar_one_or_none()
            if conv is not None:
                conv.last_message_at = datetime.now()
            await session.flush()
            return orm.id
