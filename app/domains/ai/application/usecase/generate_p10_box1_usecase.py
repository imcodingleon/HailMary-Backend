"""도윤 P-10 box1 AI 호출 UseCase."""

from __future__ import annotations

import logging

from app.domains.ai.domain.port.ai_client_port import AIClientError, AIClientPort
from app.domains.ai.domain.service.doyoon_p10_box1_prompt import (
    build_p10_box1_prompt,
    validate_p10_box1,
)
from app.domains.ai.domain.templates.doyoon_p10_box_letter import (
    get_doyoon_box1_facts,
)

logger = logging.getLogger(__name__)
DOYOON_P10_MODEL = "claude-sonnet-4-6"
# 옵션 수 따라 동적 토큰. 4 옵션 시 ~900자 보존 위해 max 1500 토큰.
_MAX_TOKENS = 1500
_TEMPERATURE = 0.85


def _mask(name: str) -> str:
    return name[0] + "**" if name else ""


class GenerateP10Box1UseCase:
    def __init__(self, *, ai_client: AIClientPort) -> None:
        self._ai_client = ai_client

    async def execute(
        self,
        *,
        user_name: str,
        ilgan: str,
        step1: tuple[str, ...],
        peak_labels: tuple[str, str] | None = None,
    ) -> str:
        facts = get_doyoon_box1_facts(
            user_name=user_name, ilgan=ilgan, step1=step1, peak_labels=peak_labels
        )
        rule_fallback: str = facts["rule_text"]
        try:
            system, user = build_p10_box1_prompt(facts)
            ai_text = await self._ai_client.generate_chapter(
                system_prompt=system, user_prompt=user,
                max_tokens=_MAX_TOKENS, temperature=_TEMPERATURE,
                model=DOYOON_P10_MODEL,
            )
        except AIClientError as exc:
            logger.warning("doyoon_p10_box1 실패 → 룰 (user=%s, exc=%s)", _mask(user_name), exc)
            return rule_fallback
        ok, reason = validate_p10_box1(ai_text, facts)
        if not ok:
            logger.warning("doyoon_p10_box1 검증 실패 → 룰 (user=%s, reason=%s)", _mask(user_name), reason)
            return rule_fallback
        return ai_text
