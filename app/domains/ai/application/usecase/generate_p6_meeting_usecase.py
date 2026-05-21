"""도윤 P-6 ai_meeting AI 호출 UseCase."""

from __future__ import annotations

import logging

from app.domains.ai.domain.port.ai_client_port import AIClientError, AIClientPort
from app.domains.ai.domain.service.doyoon_p6_meeting_prompt import (
    build_p6_meeting_prompt,
    validate_p6_meeting,
)
from app.domains.ai.domain.templates.doyoon_p6_destined import (
    get_doyoon_p6_meeting_facts,
)

logger = logging.getLogger(__name__)

DOYOON_P6_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 600
_TEMPERATURE = 0.85


def _mask(name: str) -> str:
    return name[0] + "**" if name else ""


class GenerateP6MeetingUseCase:
    def __init__(self, *, ai_client: AIClientPort) -> None:
        self._ai_client = ai_client

    async def execute(self, *, user_name: str, ilgan: str, match_slot_id: str) -> str:
        facts = get_doyoon_p6_meeting_facts(
            user_name=user_name, ilgan=ilgan, match_slot_id=match_slot_id
        )
        rule_fallback: str = facts["rule_text"]
        try:
            system, user = build_p6_meeting_prompt(facts)
            ai_text = await self._ai_client.generate_chapter(
                system_prompt=system, user_prompt=user,
                max_tokens=_MAX_TOKENS, temperature=_TEMPERATURE,
                model=DOYOON_P6_MODEL,
            )
        except AIClientError as exc:
            logger.warning("doyoon_p6_meeting 실패 → 룰 (user=%s, exc=%s)", _mask(user_name), exc)
            return rule_fallback
        ok, reason = validate_p6_meeting(ai_text, facts)
        if not ok:
            logger.warning("doyoon_p6_meeting 검증 실패 → 룰 (user=%s, reason=%s)", _mask(user_name), reason)
            return rule_fallback
        return ai_text
