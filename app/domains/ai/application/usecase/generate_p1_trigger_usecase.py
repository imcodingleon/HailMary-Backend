"""도윤 P-1 1-2 트리거 메커니즘 AI 호출 UseCase."""

from __future__ import annotations

import logging

from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_p1_trigger_prompt import (
    build_p1_trigger_prompt,
    validate_p1_trigger,
)
from app.domains.ai.domain.templates.doyoon_p1_trigger import (
    get_doyoon_p1_trigger_facts,
)

logger = logging.getLogger(__name__)

DOYOON_P1_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 500
_TEMPERATURE = 0.85


def _mask_user_name(name: str) -> str:
    if not name:
        return ""
    return name[0] + "**"


class GenerateP1TriggerUseCase:
    """P-1 ai_trigger AI 생성 + 룰 fallback."""

    def __init__(self, *, ai_client: AIClientPort) -> None:
        self._ai_client = ai_client

    async def execute(self, *, user_name: str, ilgan: str) -> str:
        facts = get_doyoon_p1_trigger_facts(user_name=user_name, ilgan=ilgan)
        rule_fallback: str = facts["rule_text"]

        try:
            system_prompt, user_prompt = build_p1_trigger_prompt(facts)
            ai_text = await self._ai_client.generate_chapter(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=_MAX_TOKENS,
                temperature=_TEMPERATURE,
                model=DOYOON_P1_MODEL,
            )
        except AIClientError as exc:
            logger.warning(
                "doyoon_p1_trigger AI 실패 → 룰 fallback (user=%s, ilgan=%s, exc=%s)",
                _mask_user_name(user_name), ilgan, exc,
            )
            return rule_fallback

        ok, reason = validate_p1_trigger(ai_text, facts)
        if not ok:
            logger.warning(
                "doyoon_p1_trigger AI 검증 실패 → 룰 fallback (user=%s, ilgan=%s, reason=%s)",
                _mask_user_name(user_name), ilgan, reason,
            )
            return rule_fallback

        return ai_text
