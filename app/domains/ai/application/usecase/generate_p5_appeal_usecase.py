"""도윤 P-5 ai_appeal AI 호출 UseCase."""

from __future__ import annotations

import logging

from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_p5_appeal_prompt import (
    build_p5_appeal_prompt,
    validate_p5_appeal,
)
from app.domains.ai.domain.templates.doyoon_p5_charm import (
    get_doyoon_p5_appeal_facts,
)

logger = logging.getLogger(__name__)

DOYOON_P5_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 550
_TEMPERATURE = 0.85


def _mask(name: str) -> str:
    return name[0] + "**" if name else ""


class GenerateP5AppealUseCase:
    def __init__(self, *, ai_client: AIClientPort) -> None:
        self._ai_client = ai_client

    async def execute(self, *, user_name: str, ilgan: str) -> str:
        facts = get_doyoon_p5_appeal_facts(user_name=user_name, ilgan=ilgan)
        rule_fallback: str = facts["rule_text"]
        try:
            system, user = build_p5_appeal_prompt(facts)
            ai_text = await self._ai_client.generate_chapter(
                system_prompt=system, user_prompt=user,
                max_tokens=_MAX_TOKENS, temperature=_TEMPERATURE,
                model=DOYOON_P5_MODEL,
            )
        except AIClientError as exc:
            logger.warning("doyoon_p5_appeal 실패 → 룰 (user=%s, exc=%s)", _mask(user_name), exc)
            return rule_fallback
        ok, reason = validate_p5_appeal(ai_text, facts)
        if not ok:
            logger.warning("doyoon_p5_appeal 검증 실패 → 룰 (user=%s, reason=%s)", _mask(user_name), reason)
            return rule_fallback
        return ai_text
