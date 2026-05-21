"""도윤 P-2 ai_recovery AI 호출 UseCase."""

from __future__ import annotations

import logging

from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_p2_recovery_prompt import (
    build_p2_recovery_prompt,
    validate_p2_recovery,
)
from app.domains.ai.domain.templates.doyoon_p2_recovery import (
    get_doyoon_p2_recovery_facts,
)

logger = logging.getLogger(__name__)

DOYOON_P2_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 700
_TEMPERATURE = 0.85


def _mask(name: str) -> str:
    return name[0] + "**" if name else ""


class GenerateP2RecoveryUseCase:
    def __init__(self, *, ai_client: AIClientPort) -> None:
        self._ai_client = ai_client

    async def execute(self, *, user_name: str, ilgan: str) -> str:
        facts = get_doyoon_p2_recovery_facts(user_name=user_name, ilgan=ilgan)
        rule_fallback: str = facts["rule_text"]
        try:
            system, user = build_p2_recovery_prompt(facts)
            ai_text = await self._ai_client.generate_chapter(
                system_prompt=system,
                user_prompt=user,
                max_tokens=_MAX_TOKENS,
                temperature=_TEMPERATURE,
                model=DOYOON_P2_MODEL,
            )
        except AIClientError as exc:
            logger.warning(
                "doyoon_p2_recovery AI 실패 → 룰 fallback (user=%s, ilgan=%s, exc=%s)",
                _mask(user_name), ilgan, exc,
            )
            return rule_fallback
        ok, reason = validate_p2_recovery(ai_text, facts)
        if not ok:
            logger.warning(
                "doyoon_p2_recovery 검증 실패 → 룰 fallback (user=%s, ilgan=%s, reason=%s)",
                _mask(user_name), ilgan, reason,
            )
            return rule_fallback
        return ai_text
