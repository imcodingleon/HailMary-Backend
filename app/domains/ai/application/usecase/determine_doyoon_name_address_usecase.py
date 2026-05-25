"""도윤 호명용 이름 분류 UseCase — AI 1회 호출 (Sonnet 4.6).

도윤 paid_report 생성 시작 시점에 1회 호출.
실명/닉네임/외래어를 판단해 호명용 이름 도출 → 모든 도윤 AI 박스에 주입.

비용: ~0.6원/결제 (도윤 총 ~220원 대비 0.3%).
"""

from __future__ import annotations

import logging

from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_name_address_prompt import (
    build_name_address_prompt,
    parse_name_address_response,
)

logger = logging.getLogger(__name__)

NAME_ADDRESS_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 200
_TEMPERATURE = 0.0   # 결정적 — 같은 입력 → 같은 출력


def _mask(name: str) -> str:
    return name[0] + "**" if name else ""


class DetermineDoyoonNameAddressUseCase:
    def __init__(self, *, ai_client: AIClientPort) -> None:
        self._ai_client = ai_client

    async def execute(self, *, user_name: str) -> str:
        """호명용 이름 결정. AI 실패 시 풀네임 fallback (안전 우선)."""
        if not user_name:
            return user_name
        try:
            system, user = build_name_address_prompt(user_name)
            response = await self._ai_client.generate_chapter(
                system_prompt=system, user_prompt=user,
                max_tokens=_MAX_TOKENS, temperature=_TEMPERATURE,
                model=NAME_ADDRESS_MODEL,
            )
            result = parse_name_address_response(response, user_name)
            logger.info(
                "doyoon name_address resolved (user=%s, result_len=%d)",
                _mask(user_name), len(result),
            )
            return result
        except AIClientError as exc:
            logger.warning(
                "doyoon name_address AI 실패 → 풀네임 fallback (user=%s, exc=%s)",
                _mask(user_name), exc,
            )
            return user_name
