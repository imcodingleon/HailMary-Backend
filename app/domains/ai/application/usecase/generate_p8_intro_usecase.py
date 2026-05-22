"""도윤 P-8 ai_intro AI 호출 UseCase."""

from __future__ import annotations

import logging
from typing import Any

from app.domains.ai.domain.port.ai_client_port import AIClientError, AIClientPort
from app.domains.ai.domain.service.doyoon_p8_intro_prompt import (
    build_p8_intro_prompt,
    validate_p8_intro,
)
from app.domains.ai.domain.templates.doyoon_p8_timing import (
    get_doyoon_p8_facts,
)

logger = logging.getLogger(__name__)

DOYOON_P8_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 500
_TEMPERATURE = 0.85


def _mask(name: str) -> str:
    return name[0] + "**" if name else ""


class GenerateP8IntroUseCase:
    def __init__(self, *, ai_client: AIClientPort) -> None:
        self._ai_client = ai_client

    async def execute(
        self, *, user_name: str, ilgan: str,
        raw_months: list[dict[str, Any]],
        start_year: int, start_month: int,
    ) -> str:
        facts = get_doyoon_p8_facts(
            user_name=user_name, ilgan=ilgan,
            raw_months=raw_months,
            start_year=start_year, start_month=start_month,
        )
        rule_fallback: str = facts["rule_text"]
        try:
            system, user = build_p8_intro_prompt(facts)
            ai_text = await self._ai_client.generate_chapter(
                system_prompt=system, user_prompt=user,
                max_tokens=_MAX_TOKENS, temperature=_TEMPERATURE,
                model=DOYOON_P8_MODEL,
            )
        except AIClientError as exc:
            logger.warning("doyoon_p8_intro 실패 → 룰 (user=%s, exc=%s)", _mask(user_name), exc)
            return rule_fallback
        ok, reason = validate_p8_intro(ai_text, facts)
        if not ok:
            logger.warning("doyoon_p8_intro 검증 실패 → 룰 (user=%s, reason=%s)", _mask(user_name), reason)
            return rule_fallback
        return ai_text
