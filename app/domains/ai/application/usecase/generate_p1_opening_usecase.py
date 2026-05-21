"""도윤 P-1 1-1 Ch1 오프닝 AI 호출 UseCase.

P-0 ai_intro 패턴 그대로. Sonnet 4.6 호출 + 검증 + 룰 fallback.
"""

from __future__ import annotations

import logging

from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_p1_opening_prompt import (
    build_p1_opening_prompt,
    validate_p1_opening,
)
from app.domains.ai.domain.templates.doyoon_p1_opening import (
    get_doyoon_p1_opening_facts,
)

logger = logging.getLogger(__name__)

# P-0/P-10과 동일 sonnet 4.6 (톤 일관성).
DOYOON_P1_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 700
_TEMPERATURE = 0.85


def _mask_user_name(name: str) -> str:
    if not name:
        return ""
    return name[0] + "**"


class GenerateP1OpeningUseCase:
    """P-1 ai_opening AI 생성 + 룰 fallback orchestrator."""

    def __init__(self, *, ai_client: AIClientPort) -> None:
        self._ai_client = ai_client

    async def execute(
        self,
        *,
        user_name: str,
        ilgan: str,
        ilju_hanja: str,
    ) -> str:
        facts = get_doyoon_p1_opening_facts(
            user_name=user_name, ilgan=ilgan, ilju_hanja=ilju_hanja
        )
        rule_fallback: str = facts["rule_text"]

        try:
            system_prompt, user_prompt = build_p1_opening_prompt(facts)
            ai_text = await self._ai_client.generate_chapter(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=_MAX_TOKENS,
                temperature=_TEMPERATURE,
                model=DOYOON_P1_MODEL,
            )
        except AIClientError as exc:
            logger.warning(
                "doyoon_p1_opening AI 호출 실패 → 룰 fallback (user=%s, ilgan=%s, exc=%s)",
                _mask_user_name(user_name), ilgan, exc,
            )
            return rule_fallback

        ok, reason = validate_p1_opening(ai_text, facts)
        if not ok:
            logger.warning(
                "doyoon_p1_opening AI 검증 실패 → 룰 fallback (user=%s, ilgan=%s, reason=%s)",
                _mask_user_name(user_name), ilgan, reason,
            )
            return rule_fallback

        return ai_text
